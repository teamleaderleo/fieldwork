# Campaign 0743: Tauri authority deny scope

State: `investigating — repair validated; packet audit active`

Issue: #743  
Parent scout: #118  
Target: `teamleaderleo/tauri`  
Exact reproduced source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Current public `dev` checked: `2f11853d2108d2790917c68f10de7a4d01a6d70f`  
Claim scope: `mechanism`  
Upstream contact authorized: `false`

## In simple words

Tauri resolves allow and deny entries with origin, window, and webview scope, but the runtime deny path discards that scope and treats any deny entry for a command as authoritative. The defect reproduces across Linux, Windows, and macOS. A narrow repair that applies the already-shipped allow applicability rule symmetrically to denies is GREEN on both the exact reproduced source and current public `dev`.

The remaining work is packet audit: retain the exact tested diff, a normal bugfix change entry, and independent review without broadening the ACL design.

## Question

Do deny rules apply only when their execution context and window/webview selectors match the caller, while a genuinely matching deny still overrides a matching allow?

## Evidence

### RED

- focused run `31328253162`: unrelated-origin and unrelated-window controls fail; matching-deny precedence passes;
- core matrix run `31328253164`: same result on all-features Linux, Windows, and macOS while nearby existing tests pass.

### Exact-pin GREEN

Run `31328772079` applies the candidate to `34ec18ba...` and passes:

- all unchanged behavior controls;
- matching-deny precedence;
- diagnostic consistency.

### Current-dev GREEN

Current public `dev` is `2f11853d...`; the authority implementation is unchanged from the reproduced source.

Run `31329554031` passes:

- deterministic candidate application;
- rustfmt;
- direct origin/window/webview controls;
- mixed deny list with unrelated plus matching denies;
- resolver-level capability controls through `Capability` → `Manifest` → `Resolved::resolve` → `RuntimeAuthority`;
- diagnostic consistency;
- diagnostic reference provenance;
- nearby `ipc::authority::tests`;
- focused clippy with warnings denied.

The edge suite establishes that unrelated origin/window/webview denies do not veto a caller, while a matching deny remains authoritative even when unrelated denies are present.

## Candidate invariant

One internal applicability predicate:

```text
origin matches command context
AND
(webview selector matches OR window selector matches)
```

Use it for:

- deny selection;
- allow selection;
- debug deny selection.

The diagnostic path cites only deny entries that actually matched and preserves existing wording for a genuine explicit deny.

## Packet audit

Owned-fork run `31329737969` adds:

- `git diff --check` on the transformed source;
- exact printed `authority.rs` diff;
- the already validated formatting, behavior, diagnostic, authority-unit, and clippy gates.

The human-facing packet should contain only:

- shared matcher and three call-site uses;
- regression tests;
- `tauri` `patch:bug` change entry;
- exact receipts and limitations.

Research transformers, runner workflows, and execution markers are evidence carriers only and must not enter the human patch.

## Stop condition

Stop technical expansion after the exact-diff receipt and independent diff review unless either exposes a semantic contradiction. No automated upstream interaction is authorized or performed.
