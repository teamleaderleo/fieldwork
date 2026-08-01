# Receipt — Go 1.26 command-golden comparison

Date: `2026-08-01`

## Purpose

Compare the current checks-disabled Go 1.26 package with a checks-enabled candidate that updates the one changed command golden. Require the installed binaries to be byte-identical.

## Identities

- Baseline source: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Candidate source: `3a036ab91fa1de2fbbd038b2b212552cff1cc5bf`
- Candidate relation: one commit, one file
- Carrier branch: `p0/435-unit-22-go126-golden-execution`
- Carrier head: `9bdb7ce730010ac953e4f6d66cba752bdfb9449a`
- Pull request: `teamleaderleo/fieldwork#438`

## Execution

- Run: [`30692966149`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692966149)
- Job: `91350898702` — success
- Platform: macOS 14.8.7 arm64
- Runner image: `macos-14-arm64` version `20260629.0180.1`
- Nix: 2.35.1
- Go: 1.26.5

## Candidate check

```text
Running phase: checkPhase
ok github.com/princjef/gomarkdoc/cmd/gomarkdoc
```

The workflow observed exactly one gomarkdoc package result, accepted installed help output, and built the version passthru with `1.1.0`.

## Installed-output identity

The workflow ran `cmp` on the baseline and candidate executables. It passed.

Both binaries had SHA-256:

```text
b8bc993930c3a8af5ebf141d0fa5e2f422b117a420630f532296e20e4428e93e
```

Baseline store path:

```text
/nix/store/l7s8y5lc0x36his1iixqlsw7c0wsw19k-gomarkdoc-1.1.0
```

Candidate store path:

```text
/nix/store/mig240cxnr30jrxlpx9b8s92ymwrqrkj-gomarkdoc-1.1.0
```

The differing store paths reflect different derivations; the installed executable bytes are identical.

## Artifact

- ID: [`8816337182`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692966149/artifacts/8816337182)
- Name: `unit-22-gomarkdoc-go126-golden-comparison`
- Digest: `sha256:14ae794f8160a5f6c68bcf113dd430d628fa4b8399ad9ceb65f1d5f33770e5e1`
- Size: 5974 bytes
- Files: 7
- Created: `2026-08-01T09:05:53Z`
- Expires: `2026-08-31T09:05:52Z`

## Conclusion

The Go 1.26 golden repair restores selected command checks without changing the installed executable. It supersedes the Go 1.25 pin as the preferred source.

Evidence class: `target-executed comparative acceptance control`.
