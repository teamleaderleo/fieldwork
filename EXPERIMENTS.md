# Fork-Free Experiments

Fieldwork supports small, disposable experiments that do not require an upstream fork, campaign, or issue.

Use this layer to answer a bounded technical question quickly: test a protocol assumption, reduce a failure, compare behaviours, exercise an API boundary, validate generated code, or build a synthetic reproduction.

## When to use a playground

Use `playgrounds/` when all of the following are true:

- the work can be performed against synthetic, public, or locally generated inputs;
- no upstream repository must be modified;
- one worker can own the experiment;
- the question is narrow enough to stop after a small result;
- the experiment does not require secrets, production systems, or unsolicited external interaction.

A playground does not need its own GitHub issue. It does need a durable result when its conclusion will be reused, cited, compared, or handed to another worker.

## Directory convention

```text
playgrounds/EXP-YYYYMMDD-short-name/
├── README.md
├── experiment.json
├── run.py | run.sh | run.ts
├── fixtures/
├── src/
├── results/
│   ├── latest.json
│   └── notes.md
└── artifacts/
```

Only create the directories the experiment actually needs. Small experiments may contain only `README.md`, `experiment.json`, and one runnable file.

## Required experiment contract

`experiment.json` records:

- stable experiment ID;
- one concrete question;
- owner or worker identity;
- creation date;
- source revisions, package versions, and retrieval boundaries;
- exact command used to run the experiment;
- expected observations or distinguishing outcomes;
- stop condition;
- network policy;
- upstream-contact authorization, always `false` unless explicitly changed by the user;
- state: `draft`, `running`, `complete`, `negative-result`, `blocked`, or `promoted`.

Use `templates/experiment.json` and `templates/experiment.md`.

## Canonical cases

Before inventing inputs, check `playgrounds/cases/`. The case packs cover broadly reusable boundaries such as:

- empty, null, zero, and missing values;
- Unicode, combining marks, emoji, newlines, and control characters;
- malformed, truncated, duplicated, and reordered input;
- nested and oversized structures;
- timeout, cancellation, retry, and partial-success paths;
- concurrent ordering and idempotency;
- filesystem and path edge cases;
- state recovery after interruption.

Not every experiment needs every category. Select cases that can distinguish the current hypotheses.

## Execution rules

- Prefer a zero-dependency runner or a pinned lockfile.
- Record the exact command, environment, and versions.
- Default to no network access.
- Use temporary directories for mutable state.
- Never use real credentials or production data.
- Retain raw output when interpretation could be disputed.
- Do not silently overwrite a result used by another report; preserve the prior run or record the changed revision.
- Generated code remains a candidate until the experiment demonstrates the claimed behaviour.

## Results

A useful result states:

1. what was tested;
2. the exact environment and revision;
3. what happened;
4. which hypothesis the evidence supports or weakens;
5. uncertainty and untested boundaries;
6. whether the result should be discarded, retained, repeated, or promoted.

Use `templates/experiment.md` for the human-readable record. Machine-readable output may live beside it.

## Promotion rules

Promote a playground when it stops being disposable:

- **to a finding** when it reveals an observation worth retaining;
- **to a probe result** when it belongs to a batch;
- **to a campaign lane** when it gains dependencies, parallel work, or sustained scope;
- **to a regression fixture** when it should protect future Fieldwork tooling;
- **to an upstream packet** only after deliberate review and explicit authorization.

Promotion preserves the experiment ID, source revision, commands, and result paths.

## Cleanup

Disposable experiments may be deleted before merge. Retained experiments should be compact and reproducible. Do not keep dependency caches, generated build trees, large binaries, credentials, or irrelevant logs in the repository.
