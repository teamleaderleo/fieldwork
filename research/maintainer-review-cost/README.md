# Maintainer Review Cost

## Question

What practical evidence helps an unfamiliar contributor lower the cost and risk of reviewing a change?

## Possible indicators

- number of clarification rounds;
- time spent reconstructing the reproduction;
- reviewer requests already answered by the initial packet;
- number and severity of defects caught during review;
- change size and conceptual surface;
- CI coverage versus claims requiring judgement;
- time to a confident accept, decline, or redirection decision;
- maintenance obligations introduced after merge.

These indicators are contextual. They should not be collapsed into a universal score.

## Working hypotheses

- A minimal failing test often provides more value than a long explanation.
- Exact revisions and commands reduce avoidable back-and-forth.
- Small changes with explicit non-goals are easier to assess.
- Design-sensitive changes benefit from early discussion before code.
- AI disclosure matters less than demonstrated ownership and verifiability, except where project policy sets stricter rules.

## Risks

- measuring public response without access to actual reviewer time;
- confusing response latency with review difficulty;
- rewarding trivial changes because they merge quickly;
- treating maintainers as a homogeneous group;
- turning the research into contribution optimisation rather than useful engineering.
