# Campaign 0743: Tauri authority deny scope

State: `claimed`

Issue: #743  
Parent scout: #118  
Target: `teamleaderleo/tauri` from exact public source `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Claim scope: `mechanism`  
Upstream contact authorized: `false`

## In simple words

Tauri retains origin, window, and webview scope on both allowed and denied commands, but the current runtime deny branch appears to discard that scope and deny whenever any deny entry exists for the command. The question is whether this over-denies callers outside the deny rule's intended boundary.

## Question

Do deny rules apply only when their execution context and window/webview selectors match the caller, while a genuinely matching deny still overrides a matching allow?

## Current evidence

- `source-established`: allow and deny entries use the same resolver and carry the same scope metadata.
- `target-test-prepared`: three deterministic controls cover other-origin, other-window, and matching-deny precedence.
- Owned-fork RED carrier: `teamleaderleo/tauri#1`; no execution receipt exists yet.

## Next discriminator

Execute the three controls against the exact target. If RED as predicted, compare a scope-symmetric deny predicate with current matching-deny precedence and diagnostic wording.

## Stop conditions

- target-executed reproduction plus repair validation;
- negative result exposing a missed surrounding invariant;
- exact overlap with newer work that already owns the behavior.

Do not broaden into an ACL redesign and do not contact upstream.