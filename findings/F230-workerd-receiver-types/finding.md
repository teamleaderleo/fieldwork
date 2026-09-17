# F230: Preserve Workerd receiver requirements in generated TypeScript

Finding state: `research-active`

Workstream: `B — Browser, web tooling, and runtime boundaries`  
Canonical Fieldwork issue: `#230`  
Canonical implementation: `teamleaderleo/workerd#1`  
Exact implementation head: `54926f86c95185a7b83b2bf1ea901c35876a9a58`  
Exact base revision: `6aa890be9fa547e3907c805b312e39917a274221`  
Strongest evidence class: mixed `target-executed` and `source-read`; current head has a known source defect  
Current review disposition: `REPAIR`  
Desk routing: `Review Queue #213; not eligible for Delivery Desk advancement`  
Upstream contact authorized: `no`  
Historical public interaction: `cloudflare/workerd#6904`; no follow-up authorized

## In simple words

Some Workerd APIs only work when called with the correct object as `this`. JavaScript enforces that at runtime, but generated TypeScript definitions can forget to tell the type checker.

The candidate adds receiver-aware declarations so TypeScript can catch more invalid rebinding. During review, one generic replacement case was found where the generated declaration can mention a type parameter that the replacement class never declares. That makes the current exact head unsafe to promote.

## Why we care

Missing receiver requirements let incorrect calls compile and then fail at runtime. Generated types are part of the developer contract, so they should describe native receiver constraints accurately.

The repair also must preserve valid handwritten overrides, global Worker APIs, static methods, and generic specialization. A type-generation fix that emits invalid TypeScript merely moves the failure earlier and breaks declaration consumers.

## What happens if we leave it alone

Without receiver-aware types, code can detach or rebind native methods in ways Workerd rejects only at runtime. With the current candidate unchanged, a generic generated owner fully replaced by a nongeneric override can emit `this: Owner<T>` while declaring no `T`, producing an invalid or misleading declaration.

The runtime mitigation in the owned testbed remains useful. The generated-types candidate cannot advance until the replacement defect is repaired.

## Current finding

Receiver requirements should be generated for non-static JSG methods, preserved through override merging and full replacement, widened only where Worker-global extraction intentionally supports bare calls, and omitted for static methods.

For a full replacement, receiver specialization must use only the type parameters actually emitted by the replacement declaration. A nongeneric replacement must not inherit undeclared generic parameters from the generated owner.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Workerd runtime receiver checks can reject detached calls that declarations permit. | `integration-executed` and `source-read` | Stensibly mitigation/regression and Workerd source investigation | Does not measure ecosystem frequency |
| Receiver annotations improve static diagnostics but contextual widening can erase them. | `target-executed` | Candidate call matrix | Runtime protection remains required |
| Lexical heritage resolution bug was repaired at the current head. | `source-read` and focused test prepared/executed history | PR #1 exact-head diff and regression | Current head still has separate generic replacement defect |
| Generic generated owner to nongeneric full replacement can emit undeclared `T`. | `source-read` complete-diff review | `preserveReplacementReceivers()` path at `54926f86...` | Needs repaired head and execution |

## System and ownership map

- JSG metadata generates TypeScript class and interface declarations.
- Override compilation and transformation merge handwritten TypeScript with generated declarations.
- Receiver provenance must survive overload merging, renaming, and full replacement.
- Worker-global extraction inlines selected members into ambient global declarations and may intentionally widen generated receivers.
- Static members and explicit custom receivers have different contracts and must remain distinct.

## Historical precedent

### Workerd handwritten TypeScript override machinery

- Source: https://github.com/teamleaderleo/workerd/blob/54926f86c95185a7b83b2bf1ea901c35876a9a58/src/workerd/api/ts/transform/override.ts
- Revision: `54926f86c95185a7b83b2bf1ea901c35876a9a58`
- Principle supported: Workerd already corrects and enriches generated declaration fidelity through explicit overrides and defines.
- Important difference: receiver policy introduces ownership and generic-specialization requirements that the earlier override machinery did not need to preserve.

### TypeScript `this` parameters

- Source: https://www.typescriptlang.org/docs/handbook/2/functions.html#declaring-this-in-a-function
- Principle supported: a declaration can express the required receiver without changing runtime call arguments.
- Important difference: Workerd generates and transforms declarations across overrides and ambient globals, so a local handwritten example does not settle transformation correctness.

### Submitted Workerd receiver-requirements issue

- Source: https://github.com/cloudflare/workerd/issues/6904
- Date: submitted before this canonical finding; open at the 2026-07-31 review.
- Principle supported: the runtime/declaration mismatch is independently recorded on the public target.
- Important difference: the issue does not establish the owned prototype's generic replacement correctness or authorize any follow-up contact.

## Approaches considered

### Retained approach: generated receiver metadata carried through transformations

This keeps native ownership requirements close to the generated method and lets override/global passes make explicit, testable decisions.

### Declined: rely only on runtime checks

Runtime protection remains necessary, yet it gives developers later feedback and misses the opportunity for accurate generated API diagnostics.

### Declined: specialize replacement receivers from generated owner parameters

A full replacement emits the replacement's type parameters. Using hidden generated parameters can create undeclared identifiers.

### Deferred: broad receiver widening to make more calls compile

Widening beyond intentional Worker-global extraction weakens the ownership contract and can hide invalid rebinding.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Non-static generated methods | Generator tests | Receiver emitted |
| Static methods | Static controls | Receiver omitted and excluded from global extraction |
| Explicit `this: void` | Override tests | Preserved |
| Custom receiver union | Override tests | Preserved |
| Generic override owner | Generic tests | Specialized when replacement declares parameters |
| Worker-global bare/nullish/`globalThis`/`self` calls | Call matrix | Intended widening covered |
| Same unqualified superclass name in another namespace | Lexical regression | Checker-first resolution selects lexical declaration |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Generic generated owner to nongeneric replacement | Known blocker | Must be added to repaired head |
| Generic generated owner to generic replacement | Missing matrix control | Must be added to repaired head |
| Nongeneric generated owner to generic replacement | Missing matrix control | Must be added to repaired head |
| Representative generated API compatibility sweep | Candidate still defective | Run after repair |
| Contribution policy and AI disclosure | Submission preparation stage | Check only after technical acceptance |
| Public upstream PR or issue follow-up | Unauthorized | Requires exact user authorization |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/workerd@54926f86c95185a7b83b2bf1ea901c35876a9a58` | Lint run `30557900133` | GitHub Actions | Passed | `target-executed` |
| Same head | Focused `30557899918`, Tests `30557899889`, Coverage `30557900238`, CodSpeed `30557899299` | GitHub Actions | Queued at last retained inspection | none |

Queued or green jobs cannot clear the source defect.

## Complete-diff and compatibility review

The current exact head contains useful receiver generation, global extraction, static controls, lexical resolution, and call-matrix coverage. Complete-diff review found one concrete defect in full-replacement generic specialization.

Smallest repair:

1. specialize a replacement receiver only from `override.typeParameters` actually emitted;
2. leave a nongeneric replacement receiver unspecialized;
3. add the three generic/nongeneric replacement controls;
4. rerun focused and ordinary exact-head gates;
5. repeat independent complete-diff review.

## Current disposition and desk routing

- Finding state: `research-active`
- Review disposition: `REPAIR`
- Review Queue entry: #213 retains the blocker
- Delivery lane: `not-entered` for advancement; existing campaign tracking may remain visible
- Exact next transition: implement the narrow generic full-replacement repair and three-case matrix
- Clearing condition: repaired exact head with focused/native execution and independent review
- Autonomous work remaining: source repair, three-case matrix, target execution, and exact-head review
- Non-delegable human decision: none

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-29 | Workerd PR #1 early candidate | Receiver generation and override/global behavior established |
| 2026-07-30 | Lexical repair head | Checker-first heritage resolution fixed same-name namespace ambiguity |
| 2026-07-30 | Complete-diff review at `54926f86...` | Generic full-replacement defect changed disposition from cleared to `REPAIR` |
| 2026-07-31 | Canonical protocol audit | Separated current no-contact authority from historical public issue #6904 and removed the false human-decision route |

## References

- https://github.com/teamleaderleo/fieldwork/issues/230
- https://github.com/teamleaderleo/workerd/pull/1
- https://github.com/teamleaderleo/fieldwork/pull/232
- https://github.com/cloudflare/workerd/issues/6904
- https://github.com/teamleaderleo/workerd/blob/54926f86c95185a7b83b2bf1ea901c35876a9a58/src/workerd/api/ts/transform/override.ts
- https://www.typescriptlang.org/docs/handbook/2/functions.html#declaring-this-in-a-function
- Workflow runs `30557900133`, `30557899918`, `30557899889`, `30557900238`, `30557899299`
