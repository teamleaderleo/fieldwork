# Charter

## Mission

Fieldwork is a public R&D notebook for understanding consequential software systems and producing defensible upstream work when that work serves a real purpose.

The repository is not a contribution scoreboard, a generic issue-hunting operation, or a machine for manufacturing pull requests.

## Commitments

### Work from genuine questions

A campaign begins with an observed failure, missing capability, interoperability problem, security concern, performance question, or research hypothesis. Popularity alone is not a reason to work on something.

### Preserve the research trail

Record the source state, reproduction, hypotheses, experiments, alternatives, uncertainty, and final decision. A rejected hypothesis or abandoned patch can still be a useful result.

### Keep humans accountable

AI systems may search, explain, generate candidates, run experiments, and challenge reasoning. A named human owns the claims, verifies the evidence, reviews every submitted change, and remains able to defend it.

### Minimise unsolicited review cost

Do not open speculative implementations against unfamiliar projects. Establish the problem, inspect prior discussion, understand project policy, and seek direction when the design is consequential.

### Contact upstream deliberately

Quiet observation is the default. External issue and pull-request links are backlink-suppressing until contact is intentional. Do not ping maintainers merely to create visibility.

### Prefer bounded, reversible work

Each campaign states its scope, stop conditions, risks, and recovery path. Large ideas should be separated into reviewable slices.

### Report negative results

A campaign may conclude that the suspected bug is expected behaviour, the proposed fix is unsafe, the upstream project is unreceptive, or the cost exceeds the value. Record that outcome plainly.

## Non-goals

Fieldwork does not exist to:

- optimise for contribution counts, stars, grant eligibility, or profile decoration;
- flood projects with generated issues, patches, comments, or review requests;
- disguise AI assistance where disclosure is expected;
- treat passing tests as sufficient proof of correctness;
- copy complete upstream repositories into this repository;
- turn every observation into an upstream interaction;
- spend days on work we would not otherwise value merely because a famous project is involved.

## Standard of evidence

Claims should be supported by the strongest practical combination of:

- minimal reproductions;
- failing and passing tests;
- exact source revisions;
- traces, logs, or protocol transcripts;
- benchmarks with declared environments;
- specification or policy references;
- compatibility matrices;
- adversarial and regression cases;
- documented uncertainty and rejected alternatives.

## Success

A successful campaign leaves the next person with a clearer model of the system. A merged patch is one possible outcome, not the definition of success.
