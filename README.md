# Arize Singapore Workshop

A hands-on workshop for tracing and evaluating an LLM agent with
[Arize AX](https://arize.com). You build a **LangGraph customer-support agent**
for a fictional outdoor retailer (Sunrise Outfitters), trace it into Arize,
chat with it through a Gradio UI, and run evaluations two ways.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hakantekgul/arize-singapore-workshop/blob/main/notebook/arize_workshop.ipynb)

## What you'll learn

1. Build a tool-using agent with LangGraph + OpenAI.
2. Trace the agent into Arize with one-line auto-instrumentation.
3. Inspect traces (LLM calls, tool calls, inputs/outputs) in the Arize UI.
4. Evaluate the agent two ways:
   - **Online LLM-as-a-judge** evals, set up in the Arize UI over live traces.
   - **Offline experiments** against a dataset, using the `ax` CLI.

## The only input you need to start

An **OpenAI API key**. Tracing additionally needs an **Arize Space ID** and
**API key** (free at [app.arize.com](https://app.arize.com), under
Settings -> Space API Keys).

## Option A - Run in Google Colab (recommended for the workshop)

Click the **Open in Colab** badge above and run the cells top to bottom. The
notebook prompts for your OpenAI key first, then (for the tracing section) your
Arize Space ID and API key. A Gradio chat UI launches inline so you can chat
with the agent and watch traces appear in Arize.

## Option B - Run locally

```bash
git clone https://github.com/hakantekgul/arize-singapore-workshop.git
cd arize-singapore-workshop

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # add your OPENAI_API_KEY (+ Arize keys for tracing)
python app.py          # opens the Gradio chat UI
```

Then chat with the agent about orders `A1001`, `A1002`, `A1003`, shipping,
returns, or sizing, and view traces at [app.arize.com](https://app.arize.com)
under the `arize-singapore-workshop` project.

## Project layout

```
arize-singapore-workshop/
├── agent/
│   ├── tools.py        # mock support tools (orders, refunds, FAQ, escalation)
│   ├── graph.py        # LangGraph ReAct agent factory
│   └── tracing.py      # Arize register() + LangChain instrumentor
├── app.py              # Gradio chat UI
├── notebook/
│   └── arize_workshop.ipynb   # guided Colab notebook (same logic)
├── evals/
│   ├── dataset.json    # sample eval questions
│   ├── run_experiment.py
│   └── README.md       # ax CLI dataset + experiment commands
├── requirements.txt
└── .env.example
```

## How tracing works

LangGraph runs on LangChain runnables, so a single OpenInference instrumentor
captures the whole graph (agent reasoning, every LLM call, and every tool call):

```python
from arize.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor

tracer_provider = register(
    space_id=ARIZE_SPACE_ID,
    api_key=ARIZE_API_KEY,
    project_name="arize-singapore-workshop",
)
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
```

## Evaluating the agent

- **Online (UI):** in the Arize UI, add an LLM-as-a-judge evaluation (e.g.
  "did the agent resolve the request?" or a hallucination check) on the
  `arize-singapore-workshop` project. It runs over the traces you generate by
  chatting with the agent.
- **Offline (ax CLI):** create a dataset, run the agent over it, and upload an
  experiment. Full commands are in [evals/README.md](evals/README.md).

## Suggested workshop agenda (~45 min hands-on)

1. Intro + slides on agent observability (10-15 min).
2. Build & run the agent with no tracing (5 min).
3. Add Arize tracing and re-run; explore traces in the UI (10 min).
4. Launch the Gradio UI; everyone chats and generates traces (5 min).
5. Set up an online LLM-judge eval in the UI (5 min).
6. Run an offline experiment with the `ax` CLI (5 min).
