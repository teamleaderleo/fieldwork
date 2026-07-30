# Campaign 0010 Synthesis

## In simple words

The original defect is real, locally fixed, and now protected by a native-workerd test. workerd's generated declarations omit a receiver rule that the runtime already enforces. TypeScript can encode the direct legal calls, and the owned fork shows how to carry the rule through the declaration pipeline. The patch is promising rather than accepted: its final head has prepared fixtures and passing lint, but no current independent review or completed target-native receipt.

## Established findings

### 1. Runtime behaviour is settled

workerd and Chromium accept bare, detached, nullish, and correct-global Worker `fetch` calls while rejecting unrelated receivers. Bun and Node intentionally accept unrelated receivers. The discrepancy is a server-global compatibility choice, not a reason to change workerd runtime semantics.

### 2. The local application boundary is protected

Stensibly's wrapper invokes native fetch through `globalThis.fetch(...)`, and the merged runtime-parity suite exercises the real OAuth client path under native workerd. The local fix remains required even if generated declarations improve.

### 3. TypeScript can express the preserved-receiver call set

An explicit receiver union can accept bare and legal global forms while rejecting unrelated holders when the function retains its receiver-aware type. Receiver information may still disappear through contextual widening to a plain callback.

### 4. Generic lint is incomplete

`unbound-method` catches ordinary member extraction but misses several bare ambient assignments and can report legal mixed-receiver detachment. A complementary typed rule can be narrow in a model, but production use needs provenance or a tiny host allowlist.

### 5. A correct general generator change is more than one inserted parameter

The initial hook is small. Correctness requires receiver policy to survive:

- print-and-reparse boundaries;
- partial and full handwritten overrides;
- overload replacement;
- explicit receiver opt-outs;
- generic owner specialization;
- inherited Worker-global traversal;
- context-global widening;
- static member exclusion.

Rook's owned-fork candidate addresses those boundaries with an internal generated-receiver marker and cleanup transform.

## Reconciled declaration policy

```text
ordinary non-static JSG method
→ this: OwningType

context-global JSG operation
→ this: OwningType | typeof globalThis | null | void
   on both the interface member and extracted ambient declaration

static method or explicit this: void
→ receiver-free

legacy handwritten override without this
→ inherit generated receiver

explicit handwritten receiver
→ preserve exactly
```

## Negative results and rejected directions

- **Change Bun or Node:** rejected; their receiver-independent global is intentional.
- **Relax workerd runtime enforcement:** rejected; runtime follows its host-operation contract.
- **Use only `unbound-method`:** insufficient coverage and one known legal-pattern false positive.
- **Ship a broad custom lint rule now:** rejected pending provenance or a deliberately narrow symbol set.
- **Treat Kestrel's Stensibly PR as the implementation:** rejected; it is an archival patch/execution carrier superseded by the fork-native branch.
- **Call cancelled CI a candidate failure:** rejected; no candidate assertion completed and failed.
- **Treat green lint as acceptance:** rejected; lint does not execute the generator pipeline.

## Evidence gaps

1. exact-head synthetic generator/compiler receipt for `e7b15f8…` or its successor;
2. exact-head independent complete-diff review;
3. one completed target-native focused run, or a recorded feasibility limit and alternative retained receipt;
4. bounded compatibility measurement across representative real generated APIs;
5. current contribution-policy and AI-disclosure packet;
6. maintainer direction on the already-submitted issue, if any arrives.

## Recommended test strategy

### Development gate

Use a small synthetic test that constructs RTTI in memory, runs the real generator and transforms, captures emitted declarations, and invokes TypeScript directly against the call matrix. This should avoid `//types`, the native workerd binary, and V8 compilation.

### Integration gate

Run the workerd-owned focused targets once on the exact candidate head before upstream publication. The expensive generated-types target verifies interaction with the real declaration surface; it should not be the normal edit loop.

### Runtime gate

Keep the merged Stensibly native-workerd regression permanently. Static analysis cannot cover every hidden host rule or erased callback type.

## Current recommendation

- Local Stensibly work: complete and retained.
- Research archive: retain, then close `teamleaderleo/stensibly#483` as superseded when its useful links are indexed.
- workerd candidate: `EXECUTE`, then exact-head independent review.
- Upstream issue: remain open without additional unsolicited comments.
- Upstream pull request: draft packet only; publication requires explicit human approval after the clearing conditions pass.
