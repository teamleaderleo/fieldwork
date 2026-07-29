# Proof-Carrying Contributions

## Thesis

A contribution can carry enough reproducible evidence, scoped reasoning, and recovery information that a maintainer reviews the claim instead of reconstructing the investigation from scratch.

## Candidate components

- exact source revision;
- minimal reproduction;
- failing regression test;
- causal explanation or bounded uncertainty;
- proposed scope;
- compatibility and security analysis;
- rejected alternatives;
- verification commands and environment;
- rollback or recovery path;
- human accountability and AI disclosure.

## Questions

- Which components reduce clarification rounds?
- When does a dossier become longer than the change warrants?
- How should evidence differ for bugs, features, performance work, and security fixes?
- Can the same packet survive a rejected implementation and remain useful?
- Which evidence is machine-verifiable, and which requires judgement?

## Failure modes

- overwhelming maintainers with an essay;
- presenting generated certainty without causal proof;
- using excessive tests to obscure a weak premise;
- treating a polished packet as entitlement to review;
- retaining sensitive traces or proprietary inputs;
- optimising the packet for persuasion instead of truth.
