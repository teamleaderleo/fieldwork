# Campaign 0743: Tauri authority deny scope

State: `investigating — RED target-executed; exact-pin GREEN validated; current-dev replay active`

Issue: #743  
Parent scout: #118  
Target: `teamleaderleo/tauri`  
Exact reproduced source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Current public `dev` checked: `2f11853d2108d2790917c68f10de7a4d01a6d70f`  
Claim scope: `mechanism`  
Upstream contact authorized: `false`

## In simple words

Tauri retains origin, window, and webview scope on both allowed and denied commands, but the runtime deny branch discards that scope and denies whenever any deny entry exists for the command. The exact target reproduces that over-denial across Linux, Windows, and macOS. The narrow scope-symmetric repair now passes a focused RED→GREEN comparison on the exact source, including diagnostic consistency and matching-deny precedence.

The same repair is being replayed against the exact current public `dev` head with rustfmt, resolver-level capability controls, nearby authority tests, and clippy.

## Question

Do deny rules apply only when their execution context and window/webview selectors match the caller, while a genuinely matching deny still overrides a matching allow?

## Current evidence

- `source-established`: allow and deny entries use the same resolver and carry the same execution-context, window, and webview metadata.
- `target-executed RED`: owned-fork PR `teamleaderleo/tauri#1` runs deterministic controls against the unmodified exact target.
- Tauri core matrix run `31328253164` reproduced the same result on all-features Linux, Windows, and macOS jobs: unrelated-origin and unrelated-window controls fail, while matching-deny precedence passes. Corresponding no-default desktop jobs and unrelated build jobs remain green.
- Focused RED run `31328253162` independently reproduces the two over-denial controls.
- `target-executed GREEN`: focused run `31328772079` applies the candidate on the exact source, passes all three unchanged behavior controls (`3 passed / 0 failed`), and passes the separate diagnostic-consistency regression.
- `target-patch-prepared`: owned-fork PR `teamleaderleo/tauri#3` retains the candidate, deterministic rewrite script, and patch artifact.
- The candidate factors one `resolved_command_matches` predicate equivalent to `origin matches AND (webview matches OR window matches)` and uses it for allow, deny, and debug deny selection.
- The diagnostic path filters deny references through the same predicate, preserves the existing wording for a genuinely matching deny, and no longer labels an unrelated deny as explicit.
- A rustfmt review found one source-layout difference only; the generator was corrected without semantic change.
- Read-only refresh pins current public `dev` at `2f11853d2108d2790917c68f10de7a4d01a6d70f`; the authority code remains unchanged from the reproduced source.
- Owned-fork PR `teamleaderleo/tauri#5` replays the candidate on an isolated copy of that exact current head. Candidate application and rustfmt already pass there.
- The current-dev carrier adds resolver-level tests through `Capability` JSON semantics → permission `Manifest` → `Resolved::resolve` → `RuntimeAuthority::resolve_access`, covering unrelated remote-origin and unrelated-window denies.
- Current upstream issue/PR searches found no active record owning this exact deny-scope defect or the misleading explicit-deny diagnostic.

## Candidate invariants

1. A deny scoped to another origin must not veto this caller.
2. A deny scoped to another window or webview must not veto this caller.
3. A deny matching this caller must still override a matching allow.
4. Allow and deny selection must interpret `ResolvedCommand` scope identically.
5. Debug authorization explanations must use the same deny applicability rule as runtime authorization.
6. Explicit-deny diagnostics must cite only deny entries that actually match the caller.
7. The repair must not broaden into ACL schema or scope redesign.

## Current-dev discriminator

Require on the current-dev carrier:

- rustfmt passes after deterministic candidate application;
- direct behavior controls pass;
- resolver-level capability controls pass;
- diagnostic consistency passes;
- nearby `ipc::authority::tests` pass;
- focused clippy passes.

After that, add explicit webview-scope and mixed-deny controls, retain a normal `tauri` `patch:bug` change entry for the human packet, and complete independent exact-diff review.

## Stop conditions

- target-executed reproduction plus exact-pin and current-dev repair validation;
- a current-dev or edge-control failure exposing a missed selector, diagnostic, or precedence invariant;
- exact overlap with newer work that already owns the behavior.

Do not broaden into an ACL redesign and do not contact upstream.
