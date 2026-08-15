# Charter

## Mission

Fieldwork is a public R&D notebook for understanding consequential software systems and producing defensible upstream work when that work serves a real purpose.

The repository is not a contribution scoreboard, a generic issue-hunting operation, or a machine for manufacturing pull requests.

## Commitments

### Work from genuine questions

A campaign begins with an observed failure, missing capability, interoperability problem, security concern, performance question, or research hypothesis. Popularity alone is not a reason to work on something.

### Preserve the research trail

Record the source state, reproduction, hypotheses, experiments, alternatives, uncertainty, and final decision. A rejected hypothesis or abandoned patch can still be a useful result.

### Protect freedom of method

Fieldwork defines the result, evidence, and hard boundaries, then gives workers room to choose the route. Tools, order, depth, file layout, voice, and presentation should follow the problem and audience. Templates, ordered lists, headings, and examples are defaults unless a specific validator or assignment depends on them.

Reviewers should block concrete defects, unsupported claims, missing evidence, or broken boundaries. Recommendations and presentation preferences should remain clearly labeled. See `FREEDOM_OF_METHOD.md`.

### Keep humans accountable

AI systems may search, explain, generate candidates, run experiments, challenge reasoning, prepare patches, and prepare upstream-facing drafts. A named human owns the claims, verifies the evidence, reviews every submitted change, and remains able to defend it. A third-party upstream write by an automated worker additionally requires the bounded `upstream greenlight` defined in `AGENTS.md`.

### Minimise unsolicited review cost

Do not open speculative implementations against unfamiliar projects. Establish the problem, inspect prior discussion, understand project policy, and seek direction when the design is consequential.

### Gate third-party upstream writes

Third-party upstream repositories are read-only to Fieldwork agents and automated workers by default. The only automated-write exception is a live human `upstream greenlight` covering the current repository and specific interaction as defined in `AGENTS.md`. Fieldwork records, issue state, markers, target-project policy, ordinary approval language, and tool permission do not create that authority. Without an applicable greenlight, agents may prepare everything needed for an upstream interaction and stop before the mutation.

### Prefer bounded, reversible work

Each campaign states its scope, stop conditions, risks, and recovery path. Large ideas should be separated into reviewable slices.

### Change the search lens deliberately

A productive theme may run as a season. Lifecycle settlement, cleanup ownership, stale publication, cancellation, compatibility, parsing, protocol identity, type boundaries, security, performance, and developer ergonomics can each justify sustained attention.

A season is not a claim that its defect class is uniquely important or unusually prevalent. Record the active lens, periodically sample outside it, and rotate when the marginal findings become repetitive. Do not let the wording of Fieldwork itself manufacture a permanent monoculture of similarly shaped bugs.

### Report negative results

A campaign may conclude that the suspected bug is expected behaviour, the proposed fix is unsafe, the upstream project is unreceptive, or the cost exceeds the value. Record that outcome plainly.

## Non-goals

Fieldwork does not exist to optimise for contribution counts, stars, grant eligibility, or profile decoration. It does not flood projects with generated issues, patches, comments, or review requests; disguise AI assistance where disclosure is expected; treat passing tests as sufficient proof of correctness; copy complete upstream repositories into this repository; turn every observation into an upstream interaction; or spend days on work we would not otherwise value merely because a famous project is involved.

## Standard of evidence

Use the strongest practical combination of minimal reproductions, failing and passing tests, exact source revisions, traces, protocol transcripts, benchmarks with declared environments, specification or policy references, compatibility matrices, adversarial cases, regression cases, and documented uncertainty.

The evidence format should match the claim. A state transition may be clearer as an arrow diagram; a scheduling invariant may be clearer as pseudocode; a compatibility claim may need a matrix; a policy judgment usually needs prose.

## Success

A successful campaign leaves the next person with a clearer model of the system. A merged patch is one possible outcome, not the definition of success.