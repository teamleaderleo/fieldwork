# Mechanism report — final disposition

Status as of 2026-08-04: **COMPLETE**

## Finding

`AsyncIterableStream` acquires a `ReadableStreamDefaultReader` for async iteration. The existing implementation released that reader on normal completion, early return, and explicit iterator failure, but not when `reader.read()` rejected.

```text
reader.read() rejects
        ↓
next() exits before cleanup
        ↓
reader lock remains held
```

## Repair

The submitted patch wraps the existing read path and runs `cleanup(false)` on rejection:

```text
reader.read() rejects
        ↓
cleanup(false)
        ↓
reader released without cancellation
        ↓
original error rethrown
        ↓
iterator becomes terminal
```

## Evidence

The focused regression suite covers both helper variants and six total cases. Against the unfixed baseline, all six cases failed because the stream stayed locked. With the patch, the same cases pass while preserving the original error and the stream's errored state.

The final source was rebuilt as one signed commit and replayed onto the then-current upstream `main` before publication.

## Final source

- Signed head: `fd6335acd351b4c00824d8b2e68d1fab40053c86`
- Changed files: three
- Public issue: https://redirect.github.com/vercel/ai/issues/18370
- Public pull request: https://redirect.github.com/vercel/ai/pull/18371

## Disposition

The Fieldwork campaign is complete. The public issue and pull request are open for upstream review. No merge or follow-up upstream action was performed after submission.
