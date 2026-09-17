# Polling deadline ownership alternatives

## Decision question

Where should the SDK enforce the invariant that a result completing after the configured polling timeout cannot become the call result?

This comparison is deliberately narrower than the first-class async API design. It does not decide webhook shape, submission handles, progress callbacks, or provider specifications. It asks which layer can own one deadline consistently without creating unnecessary public surface.

## Required invariant

A candidate is viable only if it handles all of these cases:

1. polling interval exceeds the remaining deadline;
2. status request starts before the deadline and completes after it;
3. injected transport ignores its abort signal or never settles;
4. caller abort and timeout remain distinguishable;
5. late provider success cannot publish after local timeout authority;
6. provider-specific error names, response parsing, URL validation, and metadata remain intact;
7. remote provider job cancellation is not falsely implied by local settlement.

## Alternative A — provider-local repairs

Each provider creates a deadline signal, combines it with the caller signal, passes it to every delay and status request, and rejects late terminal results.

### Strengths

- smallest source movement;
- no new public API;
- provider-specific timeout and abort errors stay local;
- can ship incrementally per provider.

### Weaknesses

- repeats subtle race logic across every async provider;
- old and new providers can drift again;
- the open async-API initiative already identifies the duplicated lifecycle as a design problem;
- fixes applied only to currently-audited video providers would leave image and transcription loops semantically inconsistent.

### Best use

A bounded backport or immediate correctness repair while lifecycle ownership remains inside providers.

## Alternative B — provider-utils deadline wrapper

A shared internal utility owns local deadline settlement and supplies one combined signal to a provider's existing polling loop. Providers still own submission, status schemas, terminal mapping, and error construction.

Research branch: `teamleaderleo/ai#18`.

### Strengths

- solves never-settling or abort-ignoring injected transports through an outer race;
- centralizes elapsed-time and signal edge cases without redesigning provider specs;
- provider-specific errors remain factories supplied by each caller;
- can be adopted incrementally.

### Weaknesses

- exporting it from provider-utils creates public surface unless an internal boundary is used;
- wrapping an entire provider operation can include submission time, while existing `pollTimeoutMs` implementations usually start the clock after submission;
- detached execution can keep running after the returned promise times out if a custom transport ignores cancellation, so handlers must not leak unhandled rejections or side effects;
- risks becoming transitional API that competes with SDK-core async orchestration.

### Best use

An internal, non-exported helper or a deliberately temporary migration mechanism. The current research branch exports it only to make the design cost visible; that is not a recommendation.

## Alternative C — SDK-core async lifecycle

Split provider submission/status operations and move polling into the SDK core, as contemplated by the first-class async API work. The core owns timeout, backoff, observation, webhook selection, and settlement.

### Strengths

- one semantic contract for all async providers;
- cleanest place for user-visible polling controls and observability;
- enables submission handles and durable/webhook strategies without provider-local loops;
- provider status adapters can remain focused on protocol translation.

### Weaknesses

- provider specification change and migration cost;
- cannot be treated as a quick non-breaking fix without compatibility design;
- the current design sketch checks completed status before timeout, so centralization by itself does not guarantee correct deadline authority;
- provider-native long-poll endpoints and webhook capabilities may not fit one simple loop.

### Best use

The long-term architecture, after the deadline invariant is explicitly specified and pinned by conformance tests.

## Current recommendation

1. Treat deadline authority as a conformance invariant now, before first-class async APIs centralize existing behavior.
2. Use focused provider-native regressions as executable evidence across both legacy and newer loop families.
3. Prefer a small internal deadline mechanism over a new exported provider-utils API for any near-term cross-provider repair.
4. Keep submission time versus polling time explicit. Existing `pollTimeoutMs` naming implies the clock begins when polling begins unless documentation says otherwise.
5. Add future async-provider conformance tests covering interval overshoot, slow status fetch, never-settling transport, caller abort, and late success.

The final owning layer can change during the async-API migration. The invariant should not.
