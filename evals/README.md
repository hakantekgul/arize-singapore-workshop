# Evaluating the agent with the `ax` CLI

This folder shows the offline / regression-style eval path using the Arize
`ax` CLI. (The other path, online LLM-as-a-judge evals, is set up live in the
Arize UI on the `arize-singapore-workshop` project over the traces the agent
produces.)

## Prerequisites

```bash
# Install the CLI (one of these)
uv tool install arize-ax-cli   # or: pipx install arize-ax-cli / pip install arize-ax-cli
ax --version

# Credentials (same Space ID + API key used for tracing)
export ARIZE_SPACE_ID="U3BhY2U6..."
export ARIZE_API_KEY="ak-..."
export OPENAI_API_KEY="sk-..."        # needed to run the agent + judge
```

## Step 1 - Create a dataset in Arize

`evals/dataset.json` is a small set of customer questions with the expected
behavior for each.

```bash
ax datasets create \
  --name support-eval-v1 \
  --space-id "$ARIZE_SPACE_ID" \
  --file evals/dataset.json
```

Note the returned `DATASET_ID`.

## Step 2 - Export the dataset (to get example IDs)

The experiment runs must reference the server-assigned `example_id`, so export
the dataset first.

```bash
ax datasets export <DATASET_ID> --stdout > exported_examples.json
```

`exported_examples.json` is a JSON array where each example now has an `id`
plus the original `input` / `expected_behavior` fields.

## Step 3 - Run the agent and build a runs file

`run_experiment.py` runs the LangGraph agent over each example and grades the
reply with an LLM judge, writing `runs.json`.

```bash
python evals/run_experiment.py --dataset exported_examples.json --out runs.json
```

## Step 4 - Create the experiment in Arize

```bash
ax experiments create \
  --name react-agent-baseline \
  --dataset-id <DATASET_ID> \
  --file runs.json
```

Open the experiment in the Arize UI to inspect outputs and `correctness`
scores. To iterate (e.g. change the model or prompt), re-run steps 3-4 with a
new `--name` and compare experiments side by side.

## Comparing experiments

```bash
ax experiments list --dataset-id <DATASET_ID>
ax experiments export <EXPERIMENT_ID> --stdout | \
  jq '[.[] | .evaluations.correctness.score] | add / length'
```
