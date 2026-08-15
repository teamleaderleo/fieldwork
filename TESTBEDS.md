# Owned Repository Testbeds

## In simple words

Fieldwork may use our own repositories as controlled places to try SDKs, runtimes, tools, and design ideas in realistic applications. These trials can reveal correctness and ergonomics problems that isolated tests miss. They must remain reversible, attributable, and separate from claims about upstream projects.

## Why use a testbed

A local playground is best for one isolated property. An owned repository is useful when the question depends on:

- actual application lifecycle;
- several components interacting;
- realistic configuration and build tooling;
- user-facing API ergonomics;
- error, cancellation, retry, or recovery paths;
- deployment or packaging behaviour;
- sustained use rather than one function call;
- whether an idea feels useful enough to keep.

This is especially valuable for SDKs and developer tools, where an API can be technically correct but awkward, misleading, incomplete, or fragile in a real project.

## Selection rules

Choose a testbed that:

- naturally exercises the target behaviour;
- can be changed and rolled back safely;
- has no production dependency on the experiment;
- can use synthetic, local, or redacted data;
- has an owner who can judge whether the result is genuinely useful;
- adds evidence that a toy model cannot provide.

Do not force a target into an unrelated repository merely to manufacture a use case.

## Public and private repositories

Fieldwork is public. Do not publish private repository names, source, architecture, data, or screenshots by default.

A private testbed may be used internally, but the public Fieldwork record should contain only:

- a neutral testbed identifier;
- the minimum reproducible boundary;
- redacted or synthetic evidence;
- the result and limitations;
- confirmation that no private material was retained.

Public repositories may be named in `testbeds/registry.yml`.

## Trial record

Use `templates/integration-trial.md`. Record:

- Fieldwork target and hub;
- testbed repository or neutral identifier;
- `target:*` and `testbed:*` labels;
- exact target version or commit;
- exact testbed revision and branch;
- realistic scenario;
- baseline behaviour;
- candidate behaviour;
- commands and environment;
- correctness and ergonomics observations;
- performance or resource measurements where relevant;
- regressions and negative results;
- rollback or cleanup;
- disposition.

## Branch and change conventions

Prefer a dedicated branch such as:

```text
fieldwork/<target>/<experiment-or-campaign>
```

Do not have several agents edit the same testbed branch. Parallel approaches use separate branches and separate trial records.

A testbed change may become a real feature in the owned repository when it is independently useful. Record that decision separately from any upstream conclusion.

## Evidence boundaries

A testbed can establish:

- that an integration path is possible;
- how the API feels in a realistic application;
- whether a failure reproduces under declared conditions;
- whether a candidate design improves the testbed;
- what additional operational boundaries appear.

A testbed cannot by itself establish:

- that other users need the same change;
- that the target project promises the tested behaviour;
- that the candidate is correct across all environments;
- that upstream maintainers will accept the direction;
- that a private implementation represents a public ecosystem.

Use `INTEGRATION_CONTEXT.md` for wider claims.

## Trial outcomes

Choose one:

- discard the experiment;
- retain the testbed as a regression or example;
- keep the change as an owned-project feature;
- promote the result to a Fieldwork finding;
- open a campaign for deeper investigation;
- prepare a human-facing upstream packet;
- record a negative result.

Preparing a packet does not authorize an automated upstream mutation. A separate live human `upstream greenlight` under `AGENTS.md` is required for any automated third-party write.

## Labels

Use the external or primary system as the target label and the owned repository as the testbed label:

```text
target:vercel-ai
testbed:stensibly
```

If the owned repository itself is the subject of investigation rather than a place to test something else, use `target:<owned-repository>` instead.

## Safety

- Never use secrets, production credentials, personal data, or live financial or health records.
- Avoid paid external calls unless explicitly approved.
- Default to local or test environments.
- Record destructive operations and cleanup.
- Do not merge experimental degradation into the default branch.
- Preserve attribution when generated code or external source material is involved.
- Third-party upstream repositories are read-only by default. Any automated state-changing upstream interaction requires the bounded human `upstream greenlight` defined in `AGENTS.md`.