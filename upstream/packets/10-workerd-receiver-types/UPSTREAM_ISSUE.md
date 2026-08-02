# Upstream issue — unit 10

## Current public record

Existing issue: https://github.com/cloudflare/workerd/issues/6904  
Title: `Generated TypeScript declarations omit receiver requirements enforced by JSG/V8`  
Current observed state: open, one historical follow-up comment, no maintainer response.

The issue already satisfies workerd's discussion-first guidance for a non-trivial change. A second issue would fragment the record.

## Recommendation

**Open no new issue. Add no follow-up without explicit authorization.**

If a human authorizes a concise update after exact-head execution, use this draft:

> The owned prototype is now one clean commit on workerd release head `813c31394b9909d8f557bba14324db275bc12720`, with ten source/test files and no workflow machinery. It preserves generated receiver provenance through override and global transforms, keeps explicit receivers authoritative, specializes and renames full-replacement receiver owners from the replacement declaration, excludes static methods from ambient function extraction while preserving generated ambient constants, and resolves inherited globals through checker-guided transformed declarations.
>
> Source review also confirmed that iterator, async-iterator, dispose, and async-dispose registrations use the owning V8 signature; callable resource instances remain a separate unchanged call-signature surface.
>
> The final publication gate is exact-head focused and ordinary target execution plus representative ambient/importable generated-output review and independent complete-diff acceptance. I will not open a public pull request until those receipts are complete and the contribution is authorized.

## Public interaction history

- Issue #6904 was created before this unit assignment.
- One historical follow-up linked the detachable-method precedent and downstream research.
- This unit made no new public upstream comment, issue, branch, pull request, review, or reaction.

## Issue-first rationale

Current contribution guidance says non-trivial changes should be discussed before coding, emphasizes backwards compatibility, and says untested code should not be submitted. The existing issue covers the problem, runtime trace, bounded direction, questions, and prior art. The next useful public interaction is a tested PR or a narrowly requested maintainer answer, not another broad research comment.
