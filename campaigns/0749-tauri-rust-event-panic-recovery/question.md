# Campaign 0749: Tauri Rust event panic recovery

State: `claimed — focused repair validated`

Issue: #749  
Parent scout: #118  
Target source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Claim scope: `mechanism`  
Upstream contact authorized: `false`

## In simple words

A Rust event callback panic currently unwinds through the handlers mutex. If application code catches that panic, the mutex is poisoned and later event work can remain trapped in the pending queue. The focused repair catches user unwind while the guard is owned normally, drops the guard, flushes pending work, then resumes the original panic.

## Question

Does the validated catch/drop/flush/resume repair preserve event ordering, nested operations, one-shot cleanup, and original panic propagation across the nearby event suite?

## Existing evidence

- target-executed RED→GREEN runs `31284095629` and `31284174704`;
- target-executed `once()` cleanup control `31284550759`;
- retained regression tests and candidate patch in #721.

## Next gate

Materialize only the focused repair on the owned fork, run the nearby event test set and format/lint gates, and obtain independent review of pending ordering and panic propagation.

## Stop conditions

Stop at review-ready exact-head evidence or reopen mechanism work if broader target tests expose an ordering/cleanup regression. Keep this separate from filesystem Scope and JS-listener registries.