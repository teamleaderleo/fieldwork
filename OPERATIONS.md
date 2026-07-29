# Operations

## Intake

A lead can enter Fieldwork when it comes from:

- a problem blocking or degrading one of our projects;
- repeated friction across several projects;
- a security, correctness, or interoperability concern;
- a technical question worth answering independently of a patch;
- an upstream request that overlaps our interests;
- a broader research programme already active here.

A famous repository with an available issue is not, by itself, a lead.

## Triage

Score a lead informally across five dimensions:

1. **Intrinsic value** — would the result still matter without recognition?
2. **Reuse** — can the result improve our own work or several external users?
3. **Evidence access** — can the claim be reproduced and tested responsibly?
4. **Upstream viability** — is the project active, governed, and open to the kind of change proposed?
5. **Boundedness** — can useful progress be made without an open-ended research commitment?

Prefer leads with strong intrinsic value and evidence access. Visibility is a secondary multiplier.

## Time boundaries

Before maintainer direction, cap speculative implementation. Spend enough time to produce a credible reproduction and proposal, then pause when acceptance depends on upstream design choices.

Do not maintain more active upstream submissions than can be answered promptly and responsibly.

## Campaign states

- `observed`
- `reproducing`
- `investigating`
- `candidate`
- `seeking-direction`
- `implementing`
- `submitted`
- `merged`
- `declined`
- `withdrawn`
- `negative-result`
- `dormant`

## Stop conditions

Stop or pause when:

- the hypothesis is disproved;
- the project explicitly rejects the direction;
- the work requires access or data we do not have;
- expected benefit no longer justifies the verification cost;
- scope expands beyond the campaign question;
- another contributor has already solved the problem;
- the work becomes detached from anything we value;
- safe testing is unavailable.

## Fork conventions

- Name branches after the campaign and bounded outcome.
- Record upstream base revision in the campaign.
- Avoid long-lived forks that silently diverge.
- Keep experiments in Fieldwork when they are independent; keep modifications in the fork.
- Delete or archive superseded branches only after recording the relevant revision.

## Weekly review

Review active campaigns for:

- new evidence;
- unanswered upstream feedback;
- stale assumptions caused by upstream changes;
- excessive scope;
- candidates ready for a decision;
- leads that should be closed rather than carried indefinitely.

## Metrics

Metrics describe the work; they do not become quotas. Useful measures include:

- time from observation to reproduction;
- time spent before upstream contact;
- review iterations;
- maintainer questions answered by the initial packet;
- accepted, declined, withdrawn, and negative outcomes;
- reused fixtures, tests, or methods;
- defects caught before submission.
