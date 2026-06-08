# Online evaluators with the `ax` CLI

This folder sets up an **online evaluator** that scores the agent's live traces
continuously - the same flow as Step 6 of the workshop notebook, but runnable
from the repo. No offline dataset or experiment needed: the evaluator runs on
the traces your agent produces (from `app.py` or the notebook).

## Prerequisites

```bash
pip install arize-ax-cli
ax --version

export OPENAI_API_KEY="sk-..."         # used to create the AI integration
export ARIZE_SPACE_ID="U3BhY2U6..."
export ARIZE_API_KEY="ak-..."          # CLI auth; a developer key from
                                       # app.arize.com/admin > API Keys also works
```

## One command

```bash
python evals/setup_online_eval.py
```

This creates an OpenAI AI integration (from your `OPENAI_API_KEY`), a template
evaluator (`resolved` / `not_resolved`), and a continuous evaluation task on the
`arize-singapore-workshop` project, then triggers a run.

## What it does, step by step

```bash
# 1) Create an AI integration in Arize from your OpenAI key (powers the LLM judge)
ax ai-integrations create \
  --name workshop-openai \
  --provider openAI \
  --api-key "$OPENAI_API_KEY" \
  --enable-default-models \
  --function-calling-enabled

# 2) Create a template (LLM-as-a-judge) evaluator
ax evaluators create-template-evaluator \
  --name support-resolution \
  --space "$ARIZE_SPACE_ID" \
  --commit-message "initial version" \
  --template-name resolution \
  --template 'Customer message:\n{{input}}\n\nAgent reply:\n{{output}}\n\nDid the agent resolve the request? Answer "resolved" or "not_resolved".' \
  --ai-integration-id <AI_INTEGRATION_ID> \
  --model-name gpt-4o-mini \
  --classification-choices '{"resolved": 1, "not_resolved": 0}' \
  --include-explanation \
  --data-granularity trace

# 3) Attach it to the project as a CONTINUOUS online task
ax tasks create-evaluation \
  --name support-resolution-online \
  --task-type template_evaluation \
  --evaluators '[{"evaluator_id": "<EVALUATOR_ID>", "column_mappings": {"input": "attributes.input.value", "output": "attributes.output.value"}}]' \
  --project arize-singapore-workshop \
  --space "$ARIZE_SPACE_ID" \
  --is-continuous \
  --sampling-rate 1.0

# 4) Run it now (continuous tasks also pick up new traces automatically)
ax tasks trigger-run support-resolution-online
ax tasks list-runs support-resolution-online
```

## Iterate

```bash
ax evaluators get support-resolution                  # inspect the evaluator
ax evaluators create-template-evaluator-version ...   # ship a new prompt version
ax tasks get support-resolution-online                # task config + status
ax tasks list-runs support-resolution-online          # watch runs as data flows
```

The `{{input}}` / `{{output}}` template variables are mapped to each trace's
input/output attributes via `column_mappings`; you can fine-tune the mapping in
the Arize UI under the project's Evals tab if your span attributes differ.
