# Continued exact-head review audit — 2026-07-30

## In simple words

The OpenTelemetry scout continued to review unrelated Fieldwork work while extending its own lifecycle research. The reviews found four separate promotion gaps: an execution-carrier compiler head, observer callbacks replacing primary hydration errors, a stale Codex implementation frontier, and HTTPX cancellation evidence that stops before transport delegation.

These reviews do not authorize merges, upstream contact, or evidence upgrades.

## Fieldwork PR #168 — static coordination compiler

- reviewed head: `bfb4b25d4c94b1ade0d574ddcd574a16c6ee397d`
- disposition: `EXECUTE / HOLD promotion`

Findings:

1. the checked-in compiler still used recursive DFS while allowing 1,000 nodes, creating a Python recursion-limit boundary;
2. a temporary workflow was intended to rewrite the implementation and push the repair, so the reviewed head was an execution carrier rather than the repaired canonical source;
3. the schema's `authority.upstream_contact` boolean was a declaration, not a capability-shaped authorization envelope.

Clearing condition:

- land the iterative detector and maximum-depth regression on the canonical branch;
- remove the execution workflow;
- clarify that a bare authority boolean cannot authorize effects;
- review the new exact head.

## Fieldwork PR #159 — Zustand explicit rehydrate failure settlement

- reviewed Fieldwork head: `6dc8575d30259ead3566b7e938d48cf7ce165f41`
- reviewed owned fork head: `teamleaderleo/zustand@047425c2d909eefaf712046b4b4021062f6e8cff`
- disposition: `REPAIR`, then `EXECUTE`

Finding:

The candidate called the rehydration completion callback before returning an explicit rejected promise. If that callback threw, the callback error replaced the original storage, parse, migration, or merge error despite the stated original-error guarantee.

Clearing condition:

- add a throwing completion-callback regression;
- preserve the primary hydration error or deliberately weaken the claimed contract;
- execute the focused and existing persist suites at the repaired head.

## Fieldwork PR #157 — Codex campaign status

- reviewed Fieldwork head: `b3e256b12e6a79e976e9033e5a0fdd61463d43a4`
- stale owned-main claim: `73ae22f90300d632833f9e4a531c4dd857c5db36`
- observed owned main: `f7265553ea1510304f3091833dcbce65ef21f10c`
- disposition: `REPAIR current-state claim`

Finding:

The newer Codex change exposes deferred runtimes directly when no executable search route exists. That can move calls into the direct result/receipt path covered by the campaign. The status file therefore could not present the older implementation frontier as current without revalidating receipt coverage and direct-versus-Code-Mode identity.

Clearing condition:

- update the current owned-main revision;
- revalidate the newly direct-exposed path;
- refresh the acceptance review against the changed implementation generation.

## Fieldwork PR #173 — HTTPX async response close settlement

- reviewed Fieldwork head: `261c57fa7b67ce33499f8e5a70faec5e7d2f8c3b`
- reviewed owned fork head: `teamleaderleo/httpx@89c1a6e1a3c31669e1f95cbb56add0148ee59035`
- disposition: `EXECUTE current matrix; HOLD broad cancellation-retry contract`

Finding:

The AnyIO join design is coherent for current waiters, ordinary failure, waiter cancellation, body-read fencing, and successful idempotence.

The real default-transport pool test cancels before the wrapper invokes HTTPCore. It therefore proves retry safety only when no transport close has begun. The production patch treats cancellation at every point as retryable, including ambiguous cancellation after transport cleanup has partially or fully committed.

No retained evidence establishes that every custom `AsyncByteStream.aclose()` or HTTPCore close path is safe to invoke again after ambiguous mid-close cancellation.

Clearing condition:

- add a post-delegation cancellation control;
- record pool ownership and second-close behavior;
- narrow the cancellation claim or preserve an explicit unknown state when cleanup outcome cannot be distinguished;
- wait for the queued exact-head workflows before accepting a candidate result.

## Relationship to OpenTelemetry work

The reviews reinforce common lifecycle principles without making the projects identical:

- a completion callback must not replace the primary operation error;
- a terminal flag is not enough when callers need one shared terminal result;
- cancellation after an external effect begins may create outcome uncertainty rather than safe retry ownership;
- an execution workflow is not the canonical source change;
- authority needs identity, scope, generation, and revocation—not a permissive input boolean.

These principles informed the repaired OpenTelemetry function cleanup and trace-provider shutdown trial, but every OpenTelemetry proposal still requires its own JavaScript evidence.

## Contact boundary

No third-party upstream issue, pull request, comment, review, reaction, or direct backlink was created.
