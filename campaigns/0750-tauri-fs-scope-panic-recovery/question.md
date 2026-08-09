# Campaign 0750: Tauri filesystem Scope panic recovery

State: `claimed — focused repair validated`

Issue: #750  
Parent scout: #118  
Target source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Claim scope: `mechanism`  
Upstream contact authorized: `false`

## In simple words

Filesystem `Scope::emit` deliberately queues reentrant actions while an `emitting` flag is true. A listener panic skips the normal flag reset and pending drain and poisons the listener mutex. If the caller catches the panic, later scope events can remain stranded.

## Question

Does the focused catch/clear/drain/resume repair restore post-panic scope progress without breaking the queueing semantics that prevent reentrant callback deadlock?

## Existing evidence

- target-executed RED→GREEN run `31284564752`;
- exact regression and candidate patch retained in #721;
- source recheck confirms reset and pending drain occur only after callbacks return normally.

The earlier public reentrant-scope deadlock and its fix are adjacent precedent, not a duplicate; issue #750 keeps redirect-safe references to that completed work.

## Next gate

Materialize the validated repair on the owned fork, run nearby scope tests, and verify pending ordering, listener removal, repeated post-panic emits, and original panic propagation.

## Stop conditions

Stop at review-ready exact-head evidence or reopen mechanism analysis if broader tests expose a regression in the existing reentrancy queue design.