# Campaign 0743: Tauri authority deny scope

State: `investigating — RED target-executed; refined GREEN candidate executing`

Issue: #743  
Parent scout: #118  
Target: `teamleaderleo/tauri` from exact public source `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Claim scope: `mechanism`  
Upstream contact authorized: `false`

## In simple words

Tauri retains origin, window, and webview scope on both allowed and denied commands, but the runtime deny branch discards that scope and denies whenever any deny entry exists for the command. The prepared controls now reproduce that over-denial on the exact target across Linux, Windows, and macOS. A narrow candidate uses one shared applicability predicate for allow, deny, and debug diagnostics; matching denies still take precedence.

## Question

Do deny rules apply only when their execution context and window/webview selectors match the caller, while a genuinely matching deny still overrides a matching allow?

## Current evidence

- `source-established`: allow and deny entries use the same resolver and carry the same execution-context, window, and webview metadata.
- `target-executed RED`: owned-fork PR `teamleaderleo/tauri#1` runs three deterministic controls against the unmodified exact target.
- Tauri core matrix run `31328253164` reproduced the same result on the all-features Linux, Windows, and macOS jobs: the unrelated-origin and unrelated-window controls fail, while matching-deny precedence passes. The corresponding no-default desktop jobs remain green, as do non-desktop build jobs.
- Focused RED run `31328253162` also fails on the two over-denial controls as predicted.
- `target-patch-prepared`: owned-fork PR `teamleaderleo/tauri#3` retains the GREEN candidate, unchanged behavior controls, deterministic rewrite script, and patch artifact.
- The refined candidate factors one `resolved_command_matches` predicate equivalent to `origin matches AND (webview matches OR window matches)` and uses it for both allow and deny resolution.
- The diagnostic path now filters deny entries through the same predicate, preserves the existing external wording for a genuinely matching deny, and reports unrelated denies through the ordinary allow/not-allowed path instead of falsely calling them explicit denies.
- A new debug-only regression requires an unrelated remote deny plus a matching local allow to produce `allowed` from `resolve_access_message`.
- Read-only current-upstream refresh shows the target authority source unchanged since the exact pin; newer `dev` commits touch release/package metadata rather than this authorization path.

## Candidate invariants

1. A deny scoped to another origin must not veto this caller.
2. A deny scoped to another window/webview must not veto this caller.
3. A deny matching this caller must still override a matching allow.
4. Allow and deny selection must interpret `ResolvedCommand` scope identically.
5. Debug authorization explanations must use the same deny applicability rule as runtime authorization.
6. The repair must not broaden into ACL schema or scope redesign.

## Next discriminator

Execute the refined GREEN carrier on the exact target. Required focused result:

- all three behavior controls pass after the candidate is applied;
- the diagnostic regression passes;
- the candidate application itself is deterministic and applies exactly once.

After focused GREEN, run the ordinary Tauri core/lint/format gates on the candidate head and then replay the candidate over current upstream `dev` to prove the two unrelated post-pin commits do not change the result.

## Stop conditions

- target-executed reproduction plus focused and ordinary-gate repair validation;
- a GREEN failure exposing a missed selector, diagnostic, or precedence invariant;
- exact overlap with newer work that already owns the behavior.

Do not broaden into an ACL redesign and do not contact upstream.
