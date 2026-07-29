# Research Programmes

## In simple words

A programme is a long-lived research direction spanning several related repositories or systems. It answers **what family of problems are we responsible for understanding?** Scout lanes answer **where is the interesting work actually hiding?** Campaigns begin only after a scout finds a concrete question worth sustained investigation.

## Hierarchy

```text
programme: long-lived research direction
├── scout lane: bounded reconnaissance on one target or boundary
│   ├── finding: concrete observation
│   └── campaign: sustained question promoted from evidence
│       ├── lane
│       ├── experiment
│       └── synthesis
└── programme synthesis: cross-target conclusions and next branches
```

A programme is not a giant backlog. It carries a thesis, target set, current scouts, branching criteria, and a compact current direction.

## Labels

Each programme hub uses:

```text
type:programme
programme:<stable-slug>
state:observed | state:ready | state:investigating | state:dormant
```

Every child scout, finding, campaign, lane, decision, or synthesis carries the programme label plus the appropriate `target:*` label.

## Scout lanes

A scout lane is an ordinary `type:lane` issue whose goal is reconnaissance rather than proving a preselected bug. It must still be bounded.

A scout should produce:

1. an `In simple words` explanation;
2. exact source revision and code map;
3. entrypoints, state ownership, side effects, failure paths, and test boundaries;
4. recent change and issue context where useful;
5. at least one runnable probe, adversarial case, or realistic testbed scenario when feasible;
6. concrete branch candidates ranked by consequence and evidence;
7. explicit negative results and dead ends;
8. a recommendation: stop, retain finding, open campaign, or run another scout.

A scout is not complete merely because it read the repository.

## Branching rule

Open a child campaign only when the scout can state:

- current behavior or missing capability;
- affected user, operator, dependent component, or system property;
- likely code boundary;
- evidence that could confirm or falsify the claim;
- why the work is more than a style, lint, documentation, or speculative refactor;
- a bounded next question.

A promising area may split into several campaigns when the questions are independently answerable. Do not make several agents investigate the same vague premise.

## Concurrency

Programmes may run many scout lanes concurrently when:

- every lane has one owner and owned path;
- target revisions are explicit;
- shared files are coordinator-owned;
- each lane has a distinct question or evidence type;
- synthesis capacity is available;
- duplicate reconnaissance is stopped quickly.

There is no fixed global lane limit. The practical limit is the amount of evidence a coordinator can accept and synthesize without losing track of dependencies.

## Programme coordinator

The coordinator owns:

- programme direction and target set;
- scout dispatch and deduplication;
- target-hub consistency;
- acceptance or revision of handoffs;
- promotion into findings and campaigns;
- cross-target synthesis;
- stopping low-value branches.

Workers own only their assigned lane or experiment outputs.

## Testbeds

Owned repositories may be used as controlled field trials. Add `testbed:<slug>` only after a real trial begins. Record the target version, owned testbed revision, scenario, baseline, observed result, limitations, and rollback.

A testbed trial can establish integration behavior in that testbed. It does not establish ecosystem-wide impact or authorize upstream contact.

## Initial portfolio

The active programme registry is `programmes/registry.yml`. Programme issues are the live orientation and coordination surface; durable files preserve accepted research and synthesis.
