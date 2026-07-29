# Target Map: Biome

Repository: https://github.com/biomejs/biome

## Why it is here

Biome offers technically meaningful work across parsers, formatters, lint rules, language tooling, diagnostics, and performance. It is relevant when our JavaScript and TypeScript projects expose concrete tooling failures.

## Areas worth understanding

- parser recovery and syntax support;
- formatter stability and idempotence;
- lint-rule correctness and false positives;
- configuration migration;
- language-server behaviour;
- performance and memory regressions;
- compatibility with generated or unusual source code.

## Evidence we can produce

- minimal source fixtures;
- parser and formatter snapshots;
- idempotence tests;
- comparison corpora;
- false-positive and false-negative cases;
- benchmark baselines;
- editor protocol transcripts.

## Entry standard

A proposed rule or formatting change needs a clear language or project rationale, adversarial examples, and compatibility analysis. Avoid taste-driven changes presented as correctness.

## Stop conditions

- the request is project-specific formatting preference;
- a reproduction cannot be reduced to a stable fixture;
- the change conflicts with established formatter policy;
- the work requires learning an unrelated subsystem solely for visibility.
