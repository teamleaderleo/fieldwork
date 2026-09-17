## In simple words

A hidden HostSingleton owner has another mutation problem beyond new child Placement and reappearance. If a visible owner replaces the shared body contents with direct HTML, the hidden owner's retained child DOM node becomes detached while its Fiber stays alive. Deleting that child while the Activity remains hidden can then ask React to remove the stale node from the live body that no longer contains it.

## Exact source path

On current React source `ec61f187fe39b0aa8ec6b508f2553b2047dc30cc`:

1. an already-hidden Offscreen subtree still traverses mutation effects with `offscreenSubtreeWasHidden = true`;
2. HostComponent deletion skips ref detachment under that flag, but the physical removal path still runs;
3. a body HostSingleton is not a singleton placement/deletion scope, so its managed children use the document container as host parent;
4. DOM `removeChildFromContainer(document, child)` resolves the physical parent to `document.body` and calls `body.removeChild(child)`.

If another visible singleton owner already used `body.innerHTML` and detached `child`, that removal target is stale.

## Pressure sequence

```text
Activity A visible
  body -> child X

A hidden/released
visible owner B -> body direct HTML
  B's write detaches X
  A's Fiber for X survives

A still hidden updates body -> empty
  deletion effect for X still runs
  host parent resolves to live document.body
  X is already detached
```

The second-review verifier extends its Activity pressure patch with this sequence and requires B's visible DOM to survive the hidden deletion without a commit-phase DOM removal failure.

## Consequence for the guard idea

Skipping the HostSingleton's own hidden update and repeated release is insufficient. The ownership boundary must also cover descendant Placement and deletion while the singleton is released to another owner, plus restoration/reconciliation when ownership returns.

## Evidence

- source control flow: source-read;
- regression: target-test-prepared on `teamleaderleo/react` PR 22 until the focused workflow executes;
- public upstream contact authorized/performed: false / false.

## Disposition

**HOLD Activity source repair.** A complete design needs one policy for descendant host mutations while a persistent singleton is logically released.