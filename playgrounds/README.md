# Playgrounds

This directory is Fieldwork's fork-free experimental workspace.

A playground answers one small question with local code, synthetic fixtures, or public interfaces. It is allowed to be temporary. It is not allowed to be ambiguous about what it tested or to imply a wider production claim it did not establish.

A playground question should come from target research, an explicit assignment, or a clearly stated local hypothesis. Existing examples and case packs do not define what should be researched.

## Starting an experiment

Scaffold a minimal retained experiment:

```text
python3 scripts/new_experiment.py parser-boundary \
  --question "Does the parser preserve duplicate event ordering?" \
  --owner worker-id
```

This creates `playgrounds/EXP-YYYYMMDD-parser-boundary/` with metadata, a report stub, and an intentionally unimplemented runner.

For a wider integration claim, provide a repository-relative dossier only after the target investigation has identified the mechanism and the wider claim needing evidence:

```text
python3 scripts/new_experiment.py integration-boundary \
  --question "Does the selected boundary preserve the property identified by the scout?" \
  --owner worker-id \
  --claim-scope integration \
  --integration-context contexts/systems/example-system.md
```

Then:

1. refine the distinguishing outcomes;
2. record source revisions and environment;
3. select useful inputs from `playgrounds/cases/`;
4. implement the smallest runnable adapter or script;
5. run locally and retain the exact command and result;
6. state what the model preserves and omits;
7. mark the outcome `complete`, `negative-result`, `blocked`, or `promoted`.

No issue is required for a one-worker experiment. Create or connect a Fieldwork issue when ownership, dependencies, human decisions, parallel lanes, or later synthesis become necessary.

## Ownership

One experiment has one owner. Other workers may read it, but they should not change its question or overwrite its results without a handoff. Parallel variants use separate experiment directories and may later be synthesized.

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

List and validate the bundled packs:

```text
python3 scripts/run_playground_cases.py --list
python3 scripts/run_playground_cases.py --validate
```

An experiment adapter reads one JSON value or text fixture from standard input and writes its result to standard output. Run a case pack with:

```text
python3 scripts/run_playground_cases.py \
  --pack playgrounds/cases/json-boundaries.json \
  --adapter "python3 playgrounds/EXP-YYYYMMDD-short-name/run.py" \
  --output playgrounds/EXP-YYYYMMDD-short-name/results/latest.json
```

The runner invokes the adapter separately for each case, records exit code, stdout, stderr, duration, and timeout state, and optionally checks declared expectations.

The adapter protocol is deliberately tiny. Experiments needing richer orchestration may use their own runner while retaining the same metadata and result conventions.

## Connecting a toy model to actual use

A small test can validate a mechanism while a context dossier answers different questions:

- where the mechanism sits in a larger workflow;
- which real components or users depend on it;
- which use is documented versus illustrative;
- how failure propagates;
- how operators would observe and recover from it;
- which standards or project contracts apply.

Use `INTEGRATION_CONTEXT.md` and `templates/integration-context.md` after the target research identifies a real need for wider interpretation. There is no canonical integration example and no default mechanism to search for.

## Validation

Run before retaining an experiment:

```text
python3 scripts/validate_experiments.py
```

CI validates retained experiment metadata, all canonical case packs, and the identity-adapter smoke test.

## Boundaries

- External GitHub interaction references remain quiet under `REFERENCE_POLICY.md`.
- A playground never authorizes upstream contact.
- Network access defaults to disabled or unnecessary.
- Do not commit secrets, production payloads, dependency caches, large binaries, or generated build directories.
- Do not use the playground directory as an unbounded scratch dump.
- Do not choose a research question merely because a fixture or example already exists.
- Mechanism evidence does not establish integration or operational impact without supporting context.

See `EXPERIMENTS.md` and `INTEGRATION_CONTEXT.md` for the full protocols.
