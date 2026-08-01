# Upstream issue — unit 10

## Current public record

Existing issue: https://github.com/cloudflare/workerd/issues/6904  
Title: `Generated TypeScript declarations omit receiver requirements enforced by JSG/V8`  
State at packet creation: open, one follow-up comment, no maintainer response.

The issue already satisfies workerd's discussion-first guidance for a non-trivial change. A second issue would fragment the record.

## Recommendation

**Open no new issue. Add no follow-up without explicit authorization.**

If a human authorizes a concise update after exact-head execution, use this draft:

> The owned prototype is now rebased onto workerd main at `7cdc8c0e089287c8f3643f3a6f668ecdc221722a` with a clean ten-file source/test diff. It preserves generated receiver provenance through override and global transforms, keeps explicit receivers authoritative, excludes static members, resolves inherited globals lexically, and binds full-replacement receivers only to replacement-declared generics.
>
> The final publication gate is exact-head focused/ordinary target execution plus representative generated-output compatibility review. I will avoid opening a pull request until those receipts are complete and the contribution is authorized.

## Public interaction history

- Issue #6904 was created before this unit assignment.
- One historical follow-up linked the detachable-method precedent and downstream research.
- This unit made no public upstream comment, issue, branch, or pull request.

## Issue-first rationale

`CONTRIBUTING.md` says non-trivial changes should be discussed before coding, emphasizes backwards compatibility, and says untested code should not be submitted. The existing issue covers problem, runtime trace, bounded direction, questions, and prior art. The next useful public interaction is a tested PR or a narrowly requested maintainer answer, not another broad research comment.
