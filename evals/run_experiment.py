"""Run the support agent over an exported Arize dataset and build a runs file.

Workflow (see evals/README.md for the full sequence):

  1. Create a dataset in Arize from evals/dataset.json (via the ax CLI).
  2. Export it so every example has a server-assigned `id`.
  3. Run this script to produce runs.json (agent output + an LLM-judge eval).
  4. Upload runs.json as an experiment with the ax CLI.

Usage:

    python evals/run_experiment.py \
        --dataset path/to/exported/examples.json \
        --out runs.json

The exported dataset file is the `examples.json` produced by
`ax datasets export <DATASET_ID>`. Each example must contain `id` and `input`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from dotenv import load_dotenv

# Allow running as `python evals/run_experiment.py` from the repo root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.graph import build_agent, run_agent  # noqa: E402
from agent.tracing import setup_tracing  # noqa: E402

JUDGE_MODEL = "gpt-4o-mini"

JUDGE_PROMPT = """You are grading a customer-support agent's reply.

Customer question:
{question}

Expected behavior:
{expected}

Agent reply:
{output}

Decide whether the agent reply is correct and helpful given the expected
behavior. Respond with ONLY a JSON object of the form:
{{"label": "correct" | "incorrect", "score": <0.0-1.0>, "explanation": "<one sentence>"}}
"""


def judge(client, question: str, expected: str, output: str) -> dict:
    """Use an LLM to grade one agent reply. Returns an evaluation dict."""
    prompt = JUDGE_PROMPT.format(question=question, expected=expected, output=output)
    resp = client.chat.completions.create(
        model=JUDGE_MODEL,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"label": "incorrect", "score": 0.0, "explanation": f"Unparseable judge output: {raw}"}
    return {
        "label": data.get("label", "incorrect"),
        "score": float(data.get("score", 0.0)),
        "explanation": data.get("explanation", ""),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        required=True,
        help="Path to examples.json exported via `ax datasets export`.",
    )
    parser.add_argument("--out", default="runs.json", help="Output runs file path.")
    args = parser.parse_args()

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set. Add it to .env or export it.")

    # Trace the experiment runs too, if Arize creds are present.
    setup_tracing()

    from openai import OpenAI

    judge_client = OpenAI()
    agent = build_agent()

    with open(args.dataset) as f:
        examples = json.load(f)

    runs = []
    for i, example in enumerate(examples, start=1):
        example_id = example.get("id")
        question = example.get("input") or example.get("question")
        expected = example.get("expected_behavior", "")
        if not example_id or not question:
            print(f"  skipping example {i}: missing 'id' or 'input'")
            continue

        print(f"[{i}/{len(examples)}] {question}")
        output = run_agent(agent, question)
        evaluation = judge(judge_client, question, expected, output)
        print(f"    -> {evaluation['label']} ({evaluation['score']:.2f})")

        runs.append(
            {
                "example_id": example_id,
                "output": output,
                "evaluations": {"correctness": evaluation},
                "metadata": {"model": "gpt-4o-mini", "judge_model": JUDGE_MODEL},
            }
        )

    with open(args.out, "w") as f:
        json.dump(runs, f, indent=2)

    scores = [r["evaluations"]["correctness"]["score"] for r in runs]
    avg = sum(scores) / len(scores) if scores else 0.0
    print(f"\nWrote {len(runs)} runs to {args.out}. Average correctness: {avg:.2f}")
    print("Next: ax experiments create --name react-agent-baseline "
          "--dataset-id <DATASET_ID> --file " + args.out)


if __name__ == "__main__":
    main()
