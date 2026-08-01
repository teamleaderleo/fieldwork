# Handoff — unit 22 gomarkdoc checks

## Current disposition

`HOLD`

The clean source candidate restores the command-package checks selected by the package. The superseded full-discovery candidate ran on Linux and Darwin and failed the same two modern-Go `lang` assertions. The narrowed exact head has passed the complete Darwin fence; Linux, final packet integrity, carrier closure, independent review, and fresh-head execution remain pending.

## Exact source

- Repository: `teamleaderleo/nixpkgs`
- Branch: `fieldwork/unit-22-gomarkdoc-checks`
- Base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Head: `569c0c4d11e5a14f3fe6237c0a50dc484f80e744`
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Relation: one commit, one file
- Proposed title: `gomarkdoc: restore command checks`

## Public-head boundary

- Refreshed public head: `63c4c8011115076be7a315edd8f740fd751b168a`
- Public-head timestamp: `2026-08-01T08:02:42Z`
- Distance from candidate base: 384 commits
- Relevant overlap: none in the gomarkdoc package or Go module builder
- Current public state: gomarkdoc 1.1.0 remains command-selected with checks disabled
- Required future action: rebase and rerun exact-head gates before authorized submission

## Exact packet

- Repository: `teamleaderleo/fieldwork`
- Branch: `p0/435-unit-22-nixpkgs-gomarkdoc-checks`
- Base: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- Directory: `upstream/packets/22-nixpkgs-gomarkdoc-checks/`
- Exact head: record the final branch tip in the unit-22 comment on issue #435

## Active execution

- PR: `teamleaderleo/fieldwork#437`
- Branch: `p0/435-unit-22-execution`
- Head: `c95da0c4b3f460df9bc8f342e98d05345da66df8`
- Target run: `30690828310`
- Darwin job: `91345125710` — success
- Linux job: `91345125742` — queued at latest check
- Carrier integrity run: `30690828341`
- Carrier integrity job: `91345125771` — queued at latest check

## Executed evidence

### Retained command-package passes

- run `30598626867`: Linux job `91056349644`, Darwin job `91056349617`
- run `30598687251`: Linux job `91056528367`, Darwin job `91056528347`

Both older runs built the Go 1.25 candidate, ran only `github.com/princjef/gomarkdoc/cmd/gomarkdoc`, and produced version `1.1.0` on Linux and Darwin.

### Full-discovery negative control

- source head: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`
- carrier head: `b6003f2a3523f01880ff5690798b69afcb4e11f5`
- target run: `30674969557` — failure
- integrity run: `30674969559` — success
- Linux job: `91300175276`, artifact `8810710677`, digest `sha256:bb7ba3579d8157fa344d1a6e7ba30a5cedf1f32f4f1f1d4eb2e3b2cd077b1a75`
- Darwin job: `91300175296`, artifact `8810556627`, digest `sha256:f471756f78106e2b74945a96e5596487baa234f33c3bae83f28195f54dfa106d`

Both jobs verified the source fence and reached root, command, and formatter packages. Both failed `github.com/princjef/gomarkdoc/lang` on `[Scanner]` versus `Scanner` and `*[os.File]` versus `*os.File`.

Receipt: `receipts/2026-08-01-full-discovery-failure.md`.

### Current exact-head Darwin pass

Darwin job `91345125710` ran on macOS 14.8.7 arm64 with Nix 2.35.1 and Go 1.25.12. It established:

- exact source head and parent;
- one-file fence and `git diff --check`;
- selected command-package build and check;
- exactly one gomarkdoc package result;
- installed `gomarkdoc --help` output;
- version passthru `1.1.0`.

Artifact:

- ID `8815619734`
- digest `sha256:db5516d38b64307b5d67ffb6bc23c33028dbdeaeb2b681b60a1cc7440958021a`
- size 5478 bytes
- five files

Receipt: `receipts/2026-08-01-command-checks.md`.

## Remaining blockers

1. Linux job `91345125742` has no terminal package/check/help/version/`nixpkgs-review` receipt.
2. Carrier integrity job `91345125771` is queued and was created against the packet base present at carrier push time.
3. A final packet-tip integrity generation remains required after receipt transfer.
4. PR #437 remains open until evidence transfer is complete.
5. Independent complete-diff acceptance is pending.
6. The source base is 384 public commits behind the refreshed head; fresh-head rebase and rerun remain required before submission.
7. Hydra, ofborg, and merge-queue evidence require an authorized public Nixpkgs PR.
8. Public upstream contact authority is absent.

## Continuation sequence

1. Inspect Linux job `91345125742` and integrity job `91345125771`.
2. Preserve runner images, source controls, command-package line, installed help, version output, Linux `nixpkgs-review`, artifacts, digests, expiry, and integrity output.
3. Classify any failure by checkout, setup, source fence, package build, command test, package-count assertion, installed binary, version, review gate, artifact publication, or repository integrity.
4. Repair only from concrete terminal evidence and rerun the exact source head after any source change.
5. Update all packet surfaces and the issue #435 handoff.
6. Trigger a final carrier generation against the completed packet tip and retain its integrity result.
7. Close PR #437 after evidence transfer.
8. Obtain independent review, then rebase onto a fresh public Nixpkgs head and rerun.
9. Keep public upstream read-only until explicit authority is granted.
