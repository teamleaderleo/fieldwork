# Remote-auth stale-generation repair execution receipt

Date: 2026-09-01

Canonical owned-fork candidate: `teamleaderleo/cmux#38`.

Exact current-main chain:

```text
594eb0461e0ae4d57a99180e19097cea5e5091e0
  -> 9acafc6eaab671e56a8883da6a0cf1a9da93a0fd  RED regression only
  -> 9665956812f274a60f08c3fa9e253c93229fbab7  GREEN serialized atomic publication
```

Execution carrier: `teamleaderleo/cmux#35`.
Run: `33563343817`.
Job: `100040765285`.
Runner: Ubuntu 24.04.

## RED

The settled-owner control passed.

The overlapping current-source regression failed at the intended consequence:

```text
single-use cleanup for lease A deleted replacement lease B
```

This proves a consumed single-use generation A can remove successor B when admin publication is outside the consumer's `wsLeaseMu` owner.

## GREEN

The repair makes `writeLeaseFile` participate in `wsLeaseMu` and publishes lease JSON with a private same-directory temporary file followed by sync, close, and atomic rename.

Validation:

- focused stale-generation + settled-owner pair: 25 consecutive passes;
- full `daemon/remote` `go test ./...`: PASS;
- `cmuxd-remote` Darwin arm64 build: PASS;
- `cmuxd-remote` Darwin amd64 build: PASS;
- `cmuxd-remote` Linux arm64 build: PASS;
- `cmuxd-remote` Linux amd64 build: PASS.

Evidence class: `target-executed` / `proven-repaired-candidate`.

## Review boundary

Complete-diff self-review found the change scoped to one production owner plus the regression. Atomic rename replaces the stable directory entry rather than following a successor symlink, and the temporary file is created in the destination directory with private mode before publication. Existing RPC-client JSON publication remains outside this lease-generation transaction because it is a different artifact and is not removed by single-use lease consumption.

Next gate: independent complete-diff review and fresh upstream overlap/contribution check before any upstream-facing action.

Third-party upstream remained read-only.
