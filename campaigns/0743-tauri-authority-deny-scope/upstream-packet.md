# Upstream Packet: scope Tauri command denies to the invoking capability context

Campaign: #743  
Target: `tauri-apps/tauri`  
State: `candidate — preparation only`

> This packet is preparation-only. Fieldwork agents and automated workers must never submit, post, comment, review, react, or otherwise mutate a third-party upstream repository. A human must perform any upstream interaction manually outside Fieldwork automation.

## Proposal

I propose applying the same resolved-command applicability rule to denied commands that Tauri already applies to allowed commands, so a deny only vetoes an invocation when its origin and window/webview scope match the caller.

A genuinely matching deny will continue to override a matching allow.

## Current and proposed behaviour

```text
current deny path:
command has any deny entry
        │
        ├─ deny belongs to another origin ─┐
        ├─ deny belongs to another window ├─▶ invocation denied
        └─ deny belongs to another webview┘

proposed deny path:
for each deny entry
        │
        ├─ origin matches
        └─ window OR webview selector matches
                    │
                    ├─ yes ─▶ invocation denied
                    └─ no  ─▶ continue evaluating caller's matching allow
```

The same applicability predicate will be used for allow selection and debug deny diagnostics.

## Consequence

Observed: a capability-scoped deny for an unrelated origin or UI target can currently veto an otherwise allowed invocation. The failure reproduces for origin and target scope and is independent of platform.

The repair is an authorization-correctness change. It does not grant a command unless a matching allow entry already exists; it prevents unrelated deny entries from overriding that matching allow.

## Reproduction

```text
source revision: 34ec18ba5e1acabebd66ae79d6fc746f63d8eb96
environment: Tauri core CI on Linux, Windows, and macOS
fixture: three focused RuntimeAuthority controls
expected:
  - unrelated remote-origin deny does not block local main
  - unrelated admin-window deny does not block main
  - matching deny still overrides matching allow
actual baseline:
  - first two fail
  - matching-deny precedence passes
deterministic: yes
```

Focused RED run: `31328253162`.

Core matrix RED run: `31328253164`; the same two failures reproduce on all-features Linux, Windows, and macOS jobs while nearby existing tests pass.

## Cause

Current runtime deny selection reduces a computed origin match to deny-entry presence:

```rust
self.denied_commands
  .get(command)
  .map(|resolved| resolved.iter().any(|cmd| origin.matches(&cmd.context)))
  .is_some()
```

`Option::is_some()` preserves whether a deny vector exists, not the boolean returned by `any(...)`. The branch also omits the window/webview selector check used by the allow path.

`Resolved::resolve` routes both allowed and denied commands through the same resolver and copies the capability's execution context, window patterns, and webview patterns into each `ResolvedCommand`. Deny-side scope metadata is therefore available at the decision point.

The debug `resolve_access_message` path separately treats any command-level deny as explicit, so a behavior-only repair would leave diagnostics inconsistent.

## Invariant

A resolved command entry applies to an invocation iff:

```text
origin matches command context
AND
(webview selector matches OR window selector matches)
```

Deny wins iff at least one deny entry satisfying that predicate exists.

## Scope

```text
included:
- RuntimeAuthority command allow/deny applicability
- debug explicit-deny selection and reference provenance
- origin, window, and webview mismatch regressions
- matching-deny precedence regression
- normal Tauri patch-level change record

excluded:
- ACL schema changes
- permission-set redesign
- command scope object semantics
- new public API
- plugin-specific policy changes
- broad authorization refactors
```

## Candidate implementation

```text
owned fork: teamleaderleo/tauri
exact reproduced base: 34ec18ba5e1acabebd66ae79d6fc746f63d8eb96
exact current public dev replay base: 2f11853d2108d2790917c68f10de7a4d01a6d70f
research carriers:
  RED: teamleaderleo/tauri#1
  exact-pin GREEN: teamleaderleo/tauri#3
  current-dev validation: teamleaderleo/tauri#5
product component: crates/tauri/src/ipc/authority.rs
```

Compact implementation:

```rust
fn resolved_command_matches(command, window, webview, origin) -> bool {
  origin.matches(&command.context)
    && (command.webviews.iter().any(|w| w.matches(webview))
      || command.windows.iter().any(|w| w.matches(window)))
}
```

Use the helper for:

- deny `is_some_and(...)` selection;
- allowed-command filtering;
- debug matching-deny filtering.

For debug messages, collect only matching deny entries before calling the existing reference formatter. Preserve the existing explicit-deny wording for a genuine match.

Suggested change file:

```md
---
'tauri': 'patch:bug'
---

Fix command deny rules to respect capability origin and window or webview scope.
```

## Verification

Exact-pin GREEN run `31328772079`:

```text
unchanged behavior controls: 3 passed / 0 failed
diagnostic consistency: pass
```

Current-public-dev GREEN run `31329554031`:

```text
candidate application: pass
rustfmt: pass
direct origin/window/webview controls: pass
mixed unrelated + matching deny control: pass
Capability -> Manifest -> Resolved::resolve controls: pass
diagnostic consistency: pass
diagnostic matching-reference provenance: pass
nearby ipc::authority tests: pass
clippy -D warnings: pass
```

A final packet-audit run `31329737969` retains `git diff --check` plus the exact transformed `authority.rs` diff and repeats the focused gates.

## Tradeoffs and alternatives

A repair limited to `resolve_access` was rejected because debug authorization explanations would continue to report unrelated denies as explicit.

Treating command denies as intentionally global was rejected by source evidence: allow and deny entries are produced by the same resolver and both retain capability context, windows, and webviews.

A broader ACL redesign is unnecessary. One shared internal predicate removes the inconsistent interpretations without changing public API or capability data.

The debug path allocates a small vector of matching deny entries so the existing reference formatter can be reused and only applicable deny references are shown. This is debug-only and keeps the change narrow.

## Recovery

The candidate is localized to one internal helper, its three uses, tests, and one change record. Reverting those lines restores previous behavior without data migration or compatibility state.

## Upstream context

Read-only searches found no active Tauri issue or pull request owning this exact deny-scope defect or the misleading explicit-deny diagnostic at the time of the current-dev replay.

No automated upstream interaction occurred.

## AI assistance

AI systems performed source mapping, generated candidate code and tests, refined regressions, and coordinated owned-fork execution. Outputs were checked against:

- cross-platform RED reproduction;
- exact-source RED→GREEN comparison;
- current-public-dev replay;
- rustfmt;
- nearby authority tests;
- clippy with warnings denied;
- resolver-level capability controls;
- diagnostic edge controls.

Tauri's current contribution policy requires the human submitter to review and test all LLM-generated content before submission and prohibits using AI to respond to review comments except for translation. A human must personally inspect every submitted line, summarize the change in their own language, and handle any upstream review conversation themselves.

## Human accountability

```text
reproduced problem:           yes
reviewed every change:        pending human review
can defend implementation:    pending human review
ran stated verification:      yes, automated owned-fork receipts above
checked current policy:       yes
automated upstream write:     no
```

## Maintainer decision requested

If a human later chooses to submit this upstream, the smallest requested decision is:

> Should command-level deny entries use the same resolved origin and window/webview applicability rule as allow entries, while preserving matching-deny precedence?
