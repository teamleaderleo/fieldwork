# Current-main repair sequence

Date: 2026-07-31

1. Establish a private, version-aware core receipt decision boundary and remove compaction authority from the public DTO.
2. Wire the shared precondition into local compact, remote compact, and remote compact v2 before any replacement history is installed.
3. Replace host-only string identity with source-qualified Direct or Code Mode operation identity.
4. Carry nested Code Mode terminal and result-persistence observations through that identity.
5. Add bounded versioned replay, checkpoints, resume/fork restoration, and coverage-loss handling.
6. Integrate append acknowledgement so pre-write failure and commit-then-error ambiguity remain distinct.

Each stage receives its own source fence, exact controls, package or compile gate, and complete-diff review. No stage inherits decision authority from an unexecuted publisher.