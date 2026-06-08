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
4. Set up a **continuous online evaluator** (LLM-as-a-judge) entirely from the
   `ax` CLI, so live traces are scored automatically.

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
│   ├── setup_online_eval.py   # create AI integration + evaluator + continuous task
│   └── README.md              # ax CLI online-evaluator commands
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

Set up a **continuous online evaluator** from the `ax` CLI: it creates an AI
integration from your OpenAI key, a template (LLM-as-a-judge) evaluator, and a
continuous evaluation task on the `arize-singapore-workshop` project that scores
every new trace automatically.

```bash
python evals/setup_online_eval.py
```

Full command-by-command breakdown is in [evals/README.md](evals/README.md). (You
can also configure the same evaluator from the Evals tab in the Arize UI.)

## Suggested workshop agenda (~45 min hands-on)

1. Intro + slides on agent observability (10-15 min).
2. Build & run the agent with no tracing (5 min).
3. Add Arize tracing and re-run; explore traces in the UI (10 min).
4. Launch the Gradio UI; everyone chats and generates traces (5 min).
5. Create a continuous online evaluator from the `ax` CLI; watch it score live
   traces in the Arize UI (10 min).
