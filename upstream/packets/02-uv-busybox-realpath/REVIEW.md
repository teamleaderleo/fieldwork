# Review — Unit 02

## Disposition

`RETIRED — PUBLIC PR CLOSED WITHOUT MERGE`

## Final subject

- Public PR: [astral-sh/uv#20943](https://redirect.github.com/astral-sh/uv/pull/20943)
- Final head: `28b00fc950c7eb924ab243418d44ce16ac5bee5a`
- Branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Changed files: four
- Diff: 207 additions, 16 deletions
- Final canonical CI: run `31059965759` — success

## Review history

### Initial candidate

The first candidate removed `--` only from generated `realpath` calls and retained `dirname --`, quoting, symlink resolution, and historical launcher recognition.

Maintainer review correctly identified a missing invariant: a bare launcher operand beginning with `-` must not be reinterpreted as an option on implementations that support ordinary option parsing.

### Revised candidate

The source was reworked to probe the runtime implementation and preserve `realpath -- "$0"` when supported. BusyBox-style implementations fell back to `realpath "$0"`.

The revision added target-native controls for:

- compliant and BusyBox-style branches;
- probe and final-call arguments;
- bare `-foo`;
- a literal file named `--`;
- current and historical `python` / `python3` launchers;
- POSIX and Fish activation generation.

macOS path canonicalization and Windows Clippy import gating were repaired during CI. The final full visible workflow was green.

## Technical review result

No unresolved correctness defect was established in the final runtime-probe source.

The probe:

- observed the actual runtime `realpath` selected through `PATH`;
- required both successful status and output equal to `/`;
- preserved `--` when supported;
- avoided BusyBox's false diagnostic;
- retained symlink canonicalization and `dirname --`;
- kept migration recognition bounded to four known generated forms.

The explicit current/historical × `python`/`python3` constants are repetitive but transparent. For a fixed set of compatibility signatures, generating them through another abstraction would reduce source repetition while making the accepted formats less immediate to inspect.

## Landing decision

The final patch was not accepted because uv maintainers rejected the downstream tradeoff:

- an additional `realpath` invocation for every affected launcher execution;
- more generated shell in launchers and activation scripts;
- ongoing uv maintenance for a BusyBox conformance gap.

They selected an upstream BusyBox repair instead: [vda-linux/busybox_mirror#26](https://redirect.github.com/vda-linux/busybox_mirror/issues/26).

This distinction is important:

- **technical assessment:** the final candidate was coherent and green;
- **project decision:** the cost and ownership boundary were not acceptable to uv;
- **disposition:** retire the downstream candidate.

## Communication review

The detailed alternatives were useful research. The public reply presented the entire option tree before confirming whether runtime probing itself was acceptable.

For future upstream work:

1. read the target's contribution and AI policies before public interaction;
2. when review guidance is architecturally ambiguous, ask the smallest decision question first;
3. lead with the most relevant finding and the decision needed;
4. retain the full rejected-alternative analysis in the internal packet unless the maintainer asks for it;
5. have the contributor write the final maintainer-facing text directly and own every claim.

## Final decision

No human approval or upstream preparation remains pending.

Do not reopen, resubmit, or continue the downstream uv implementation unless maintainers explicitly request a different downstream direction. Keep the packet as negative-result evidence and a portability reference.
