# Existing issue record — Unit 02

The original public report remains [astral-sh/uv#16209](https://redirect.github.com/astral-sh/uv/issues/16209). Do not open a duplicate uv issue.

## Public history

The first public comment announced a tested downstream patch that removed `--` from generated `realpath` calls while preserving `dirname --`, quoting, symlink resolution, and historical launcher recognition.

Maintainer feedback identified the leading-hyphen operand problem. The formal pull request was then revised to preserve `--` when supported and use a runtime capability probe for BusyBox-style implementations.

The final downstream candidate passed CI but was rejected as a project tradeoff. uv maintainers do not want the extra runtime command and generated-shell complexity in affected launchers.

Public uv pull request: [astral-sh/uv#20943](https://redirect.github.com/astral-sh/uv/pull/20943) — closed without merge.

## Upstream handoff

The selected direction is to fix BusyBox `realpath` itself so it recognizes `--` as the end-of-options delimiter.

BusyBox tracker: [vda-linux/busybox_mirror#26](https://redirect.github.com/vda-linux/busybox_mirror/issues/26)

The BusyBox tracker welcomed a patch, and the uv maintainer who opened it stated that they intended to work on one. Do not create a competing patch without first checking the current issue state and ownership.

## Retained supporting evidence

The downstream investigation remains useful because it established:

- why unconditional delimiter removal weakens option safety;
- why retry fallback can duplicate command-substitution output on BusyBox;
- why `./$0` can resolve the wrong target after `PATH` lookup;
- why `command -v` does not cover sourced activation scripts;
- why generation-time detection can inspect the wrong runtime utility;
- why BusyBox name/help/symlink fingerprinting is brittle;
- that a runtime behavior probe can preserve both branches correctly;
- that uv nevertheless prefers an upstream BusyBox repair.

## Public-action ownership

The uv issue and PR interactions are complete. No additional uv comment, reaction, review, issue, or pull request is authorized by this packet.

Any future BusyBox contribution is a separate public action and requires a fresh ownership and current-state check.
