# Tests and receipts — Unit 02: BusyBox-safe relocatable launchers

## Current judgment

`READY FOR LAST-MILE LOOK`

The final source passed focused formatting, compilation, unit tests, Linux GNU behavior, Alpine BusyBox behavior, macOS behavior, direct shebang `$0` probes, exact source fencing, and source-only publication. No technical test blocker remains.

## Exact identity

- Public base/current main: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Clean source head: `c42973ef0490c75df1c7e7f4e9a54d46c6bca059`
- Clean source tree: `fdcbe687e0afaaf499e5098b3308525e03000526`
- Final execution base: `d2ebfd92457b0047a4b02e3ccb8431769e12b145`
- Final carrier head: `6fbdf4d7fb0ff577f5be24972b1a5bba73111793`
- Final execution PR: [`teamleaderleo/uv#7`](https://github.com/teamleaderleo/uv/pull/7), closed without merge
- Workflow: [`30690034279`](https://github.com/teamleaderleo/uv/actions/runs/30690034279)
- Test date: 2026-08-01

## Final workflow jobs

| Job | ID | Result | Purpose |
| --- | ---: | --- | --- |
| `source-linux` | `91342987834` | success | exact source generation, format, compile, two Rust tests, GNU/BusyBox matrices, Linux `$0` probe |
| `platform-macos` | `91342987814` | success | macOS matrix and macOS `$0` probe |
| `publish-source` | `91343684491` | success | recreate formatted candidate, exact three-file fence, one-commit publication |

## Final artifacts

| Artifact | ID | Digest |
| --- | ---: | --- |
| Linux source and receipts | `8815417615` | `sha256:6a2f205d91e2a70021cc16c8d6b4a30ee2f983a90344a88f5e9d9206d1d9dd8d` |
| macOS receipts | `8815330073` | `sha256:9f9a50fe67a2df015a17f79303f340512a35da28a0841e9ba6e9377ff0dc8b8c` |
| publication receipt | `8815424130` | `sha256:f33ce4b084c7a37dcb7cc6bacc4b2f00f8e82200294afda491d77cac2327f3d8` |

## Source gates

### Candidate and publication fences

Passed:

- carrier ancestry from public source base and execution-only base;
- exact five-file execution-carrier diff;
- Python generator syntax;
- Python argv0-probe syntax;
- POSIX matrix syntax;
- exact three-source-file generated diff;
- `git diff --check`;
- exact three-source-file published commit;
- one commit ahead and zero behind public base.

Final source files:

| File | Additions | Deletions | Blob |
| --- | ---: | ---: | --- |
| `crates/uv-install-wheel/src/wheel.rs` | 2 | 2 | `1d77576b32df7f8711b29012cf380b178d87e362` |
| `crates/uv-virtualenv/src/virtualenv.rs` | 4 | 4 | `fc79fde1dd3630a3fd529ee83a3e4bf154becaa1` |
| `crates/uv/src/commands/project/run.rs` | 59 | 7 | `7a6d980ed06a46a40cbd41e3f35fe73eac8ecd05` |

The source generator removed five generated `realpath --` and seven generated `dirname --` occurrences. One exact historical form remains deliberately inside `LEGACY_RELOCATABLE_SHEBANG` for upgrade compatibility.

### Formatting and compilation

Passed at carrier head `6fbdf4d7fb0ff577f5be24972b1a5bba73111793`:

```text
cargo fmt --all --check
cargo check -p uv-install-wheel -p uv-virtualenv -p uv
```

### Rust tests

Passed:

```text
cargo test -p uv-install-wheel test_shebang
cargo test -p uv copy_entrypoint_accepts_current_and_legacy_relocatable_shebangs
```

Results:

- wheel shebang assertion: 1 passed;
- `copy_entrypoint` current/legacy compatibility test: 1 passed;
- the compatibility test verifies both exact shebang forms, rewritten interpreter, retained script body, and executable mode `0751`.

## Launcher matrices

Every platform ran current and corrected launchers across:

- absolute path;
- relative path;
- PATH lookup;
- filename containing spaces;
- `./-tool`;
- external symlink.

Each candidate case asserted status 0, sibling fake-Python selection, argument delivery, and empty stderr.

| Platform | Current | Candidate | Result |
| --- | --- | --- | --- |
| Ubuntu 24.04 GNU coreutils | 6/6 clean | 6/6 clean | 12/12 passed |
| Alpine 3.22 BusyBox 1.37 | 6/6 success with expected `realpath: --` diagnostic | 6/6 clean | 12/12 passed |
| macOS 15 | 6/6 successful observation | 6/6 clean | 12/12 passed |

## Direct shebang `$0` discriminator

### Question

Delimiter-free GNU `realpath "$0"` parses a synthetic bare `$0=-tool` as an option. Can the actual generated shell launcher receive that value during direct shebang execution?

### Method

On Linux and macOS, a test script was executed through the operating system shebang path while the process caller requested argv0 values:

- `-tool`;
- `--help`;
- `plain-name`.

### Result

On both platforms, shell `$0` was the actual script pathname for every request. It never began with `-`.

The synthetic control remained useful:

- `realpath -- "$0"` with synthetic `$0=-tool` succeeds on GNU;
- `realpath "$0"` with synthetic `$0=-tool` fails option parsing;
- direct shebang execution replaces the synthetic value with the script path.

Conclusion: the generated launcher entry path supplies a pathname. The tested `./-tool` invocation also succeeds. No additional shell normalization branch is warranted.

## macOS discriminator

The first macOS run executed the candidate successfully but the harness compared lexical `/var/...` with canonical `/private/var/...`. The expected fake-Python path was changed to `realpath "$root/bin/python"`. The corrected run passed every current and candidate case.

This was an assertion-path issue, not a source failure.

## Setup and losing-path record

| Attempt | Observation | Classification | Disposition |
| --- | --- | --- | --- |
| workflow `30625826344` | broad generated-doc/OpenAPI gate failed outside unit files | unrelated repository gate | excluded from launcher conclusion |
| PR #5 against stale fork `main` | 244 unrelated public-history files in carrier compare | carrier setup | replaced with exact base and source fences |
| workflow `30674680508` | runner lacked rustfmt | runner setup | install component explicitly |
| workflow `30676820652` | rustfmt required braced virtualenv match arm | source formatting | final source uses braced arm |
| temporary commit `3ddcd43820b41d6752efa1ebd3f200848aee73bc` | unrelated wheel formatting drift | source exactness | rejected before canonical branch use |
| first last-mile generator draft | Python triple-quote collision | harness syntax | fixed before source execution |
| inherited isolated workflow on PR #7 | superseded publisher fired and failed its fence | carrier concurrency | disabled before final workflow |
| first macOS assertion | `/var` versus `/private/var` | harness path identity | canonical expected path; rerun passed |
| first final Linux attempt | `cargo fmt` preceded rustfmt installation | runner order | install rustfmt first; rerun passed |

## Prior retained receipts

- `30625826268` / `91140735058`: original 24/24 GNU/BusyBox behavior discriminator.
- `30650924197` / `91223680476`: original synchronized three-owner source generation, compile, and matrix.
- `30676914631` / `91305994591`: first clean current-head source publication without historical-recognizer coverage.
- Final workflow `30690034279` supersedes the source and focused test conclusion by adding migration compatibility, macOS, and direct `$0` evidence.

## Remaining optional coverage

These are reviewer choices, not current blockers:

- complete repository suite;
- full project clippy;
- FreeBSD or another BSD-family runner;
- integration-level placement for the new `copy_entrypoint` compatibility assertion.

## Reversing conditions

Reopen technical work if:

- human review rejects dual recognition of historical and corrected shebangs;
- a supported launcher entry path is shown to expose an option-like shell `$0`;
- another supported platform fails the corrected fragment;
- upstream main changes the three owners before submission;
- the complete target suite exposes a unit-related failure.
