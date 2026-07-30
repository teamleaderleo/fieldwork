# EXP-20260730-mmdebstrap-clone

## In simple words

This experiment checks whether GitHub Actions can retrieve an exact Debian `mmdebstrap` source revision from Salsa and preserve enough evidence to repeat later work from a phone-driven GitHub workflow. The job clones the public repository into temporary runner storage, verifies the requested Debian tag, records the resolved commit and source inventory, and uploads the compact evidence. The upstream source tree remains outside Fieldwork and disappears with the runner. The current step establishes the checkout path only; it does not test a bug or prepare an upstream submission.

## Question

Can a GitHub-hosted runner reproducibly clone the official Debian `mmdebstrap` repository at tag `debian/1.5.7-3`, verify the resolved commit, and retain a compact manifest without copying the upstream repository into Fieldwork?

## Source boundary

- Project: Debian `mmdebstrap`
- Repository: `https://salsa.debian.org/debian/mmdebstrap.git`
- Requested revision: `debian/1.5.7-3`
- Retrieval date: 2026-07-30
- Upstream contact authorized: false

The workflow records the full resolved commit SHA during execution. The Debian tag page identifies `debian/1.5.7-3` as the unstable release tag for version 1.5.7-3.

## Run

```sh
bash playgrounds/EXP-20260730-mmdebstrap-clone/run.sh
```

GitHub Actions runs the same command through `.github/workflows/mmdebstrap-clone.yml`.

## Expected result

The command should:

1. clone only the requested tag into a temporary directory;
2. verify that `HEAD` exactly matches the tag;
3. write `results/source-manifest.txt` containing the repository root, requested revision, full commit SHA, commit metadata, and a sorted top-level file inventory;
4. remove the temporary checkout on exit.

## Evidence boundary

A successful run proves that this GitHub-based lab can retrieve and identify this public source revision. It says nothing yet about the reported `$TMPDIR` behavior, package correctness, server-image impact, or whether Debian maintainers would accept any eventual change.

## Stop condition

Stop when one GitHub Actions run produces a verified full commit SHA and uploaded source manifest, or when the checkout fails with enough logs to identify the blocking boundary.
