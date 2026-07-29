# Playgrounds

This directory is Fieldwork's fork-free experimental workspace.

A playground answers one small question with local code, synthetic fixtures, or public interfaces. It is allowed to be temporary. It is not allowed to be ambiguous about what it tested.

## Starting an experiment

1. Copy `templates/experiment.json` and `templates/experiment.md` into `playgrounds/EXP-YYYYMMDD-short-name/`.
2. State one distinguishing question.
3. Select useful inputs from `playgrounds/cases/`.
4. Add the smallest runnable adapter or script.
5. Run locally and retain the exact command and result.
6. Mark the outcome `complete`, `negative-result`, `blocked`, or `promoted`.

No issue is required for a private one-worker experiment. Create or connect a Fieldwork issue when ownership, dependencies, human decisions, parallel lanes, or later synthesis become necessary.

## Ownership

One experiment has one owner. Other workers may read it, but they should not change its question or overwrite its results without a handoff. Parallel variants should use separate experiment directories and may later be synthesized.

## Expected contents

Minimal:

```text
EXP-YYYYMMDD-short-name/
├── README.md
├── experiment.json
└── run.py
```

Expanded:

```text
EXP-YYYYMMDD-short-name/
├── README.md
├── experiment.json
├── fixtures/
├── src/
├── results/
└── artifacts/
```

## Running canonical cases

`python3 scripts/run_playground_cases.py --list` lists the bundled case packs.

An experiment adapter reads one JSON value from standard input and writes its result to standard output. Run a case pack with:

```text
python3 scripts/run_playground_cases.py \
  --pack playgrounds/cases/json-boundaries.json \
  --adapter "python3 playgrounds/EXP-YYYYMMDD-short-name/run.py" \
  --output playgrounds/EXP-YYYYMMDD-short-name/results/latest.json
```

The runner invokes the adapter separately for each case, records exit code, stdout, stderr, duration, and timeout state, and optionally checks expectations declared by the case.

The adapter protocol is deliberately tiny. Experiments needing richer orchestration may use their own runner while retaining the same experiment metadata and result conventions.

## Boundaries

- External GitHub interaction references remain quiet under `REFERENCE_POLICY.md`.
- A playground never authorizes upstream contact.
- Network access defaults to disabled or unnecessary.
- Do not commit secrets, production payloads, dependency caches, large binaries, or generated build directories.
- Do not use the playground directory as an unbounded scratch dump.

See `EXPERIMENTS.md` for the full protocol.
