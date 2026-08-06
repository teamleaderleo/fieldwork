# Closeout brief — uv BusyBox `realpath` compatibility

## Recommendation

Retire Unit 02 as a downstream uv contribution and retain the packet as negative-result evidence.

The [public uv pull request](https://redirect.github.com/astral-sh/uv/pull/20943) closed without merge. uv maintainers prefer to repair BusyBox `realpath` upstream rather than add a runtime capability probe to generated uv launchers.

Preferred upstream repair: [vda-linux/busybox_mirror#26](https://redirect.github.com/vda-linux/busybox_mirror/issues/26)

## The user-visible problem

On Alpine and other BusyBox systems, a successful uv-generated command can print:

```text
realpath: --: No such file or directory
```

The launcher usually continues and resolves the next operand, so the defect is primarily a false error on stderr rather than a complete launch failure.

## What was submitted

### First candidate

Remove `--` only from generated `realpath` calls while retaining `dirname --`, quoting, symlink canonicalization, and current/historical launcher recognition.

Maintainer review identified a real regression risk: a bare entrypoint name beginning with `-` could be reinterpreted as an option by implementations that support ordinary option parsing.

### Revised candidate

Probe the runtime implementation with `realpath -- /`. Preserve the delimiter when the probe succeeds and returns `/`; otherwise use the BusyBox-compatible form.

The revised patch covered:

- POSIX launchers;
- POSIX and Fish activation generation;
- current and historical `python` / `python3` launcher recognition;
- compliant and BusyBox-style fake utilities;
- bare `-foo` operands;
- a literal file named `--`;
- Linux, macOS, and Windows ordinary CI.

Final public head: `28b00fc950c7eb924ab243418d44ce16ac5bee5a`  
Final canonical CI: run `31059965759` — success  
Final diff: four files, 207 additions, 16 deletions

## Why it did not land

The final patch was technically coherent and fully green, but uv maintainers rejected its tradeoff:

- one additional `realpath` invocation for each affected launcher execution;
- more generated shell in every relocatable launcher and relevant activation script;
- downstream maintenance for a BusyBox standards mismatch.

They chose to pursue `--` support in BusyBox `realpath` instead.

## What the research established

The explored alternatives were useful even though the patch was retired:

- unconditional delimiter removal weakens option safety;
- retry fallback can duplicate resolved output on BusyBox;
- `./$0` can resolve the wrong file after `PATH` lookup;
- `command -v` does not solve sourced activation scripts;
- generation-time detection can inspect the wrong runtime utility;
- BusyBox fingerprinting by name or help output is brittle;
- runtime behavior probing works, but the target project does not want its cost.

## Process takeaway

When maintainer guidance leaves a design constraint ambiguous, ask the smallest architectural question before expanding the implementation.

Private research should keep the full option tree. Maintainer-facing discussion should begin with the relevant finding and requested decision, then provide deeper alternatives only when they help the review.

Target contribution and AI policies must be checked before public replies. The contributor remains responsible for writing the final maintainer-facing message directly and understanding every technical claim.

## Final ask

No approval or public action is pending for this unit.

Keep the packet for future portability work and BusyBox context. Do not reopen or resubmit the downstream uv approach unless uv maintainers explicitly request it.
