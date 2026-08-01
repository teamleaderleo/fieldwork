# Controlled target branch receipt — 2026-08-01

## Result

The controlled mmdebstrap repository is accessible, the clean source candidate is materialized directly from the exact canonical commit, and the isolated target-repository gate passed.

This clears the former `NEEDS FORK`, missing-source-branch, and focused target-execution blockers. It does not clear upstream-native regression integration, the ordinary mirror-backed/source gate, independent final target-diff acceptance, or public-authority blockers.

## Exact source identity

- controlled repository: `teamleaderleo/mmdebstrap`
- repository permission observed: push/admin access
- canonical source base: `77ec9be5417ee44c96343d2347145585da1b1f94`
- base `coverage.py` blob: `9a522484aef05deae514a98e4b6adf5feb6c886d`
- clean source branch: `linux-fieldwork/unit-11-coverage-backend-cancellation`
- clean source head: `431614b3af58ba4f70791aa1d42cf5b71c965dd2`
- candidate `coverage.py` blob: `9e31f21cf37228257b5e0705d9ecb13b7a66e40f`
- commit message: `coverage: cancel selected backend process group on SIGINT`
- ancestry: one commit ahead of the exact base, zero commits behind
- changed-file fence: `coverage.py` only
- diff statistics: 8 additions, 3 deletions

## Exact product diff

```diff
@@ -5,6 +5,7 @@
 import os
 import sys
 import shutil
+import signal
 import subprocess
 import argparse
 import time
@@ -410,13 +411,17 @@ def main():
-        proc = subprocess.Popen(argv)
+        proc = subprocess.Popen(argv, start_new_session=True)
         try:
             proc.wait()
         except KeyboardInterrupt:
-            proc.terminate()
+            try:
+                os.killpg(proc.pid, signal.SIGTERM)
+            except ProcessLookupError:
+                pass
             proc.wait()
-            break
+            print("interrupted by SIGINT", file=sys.stderr)
+            raise SystemExit(130)
```

This is the selected retained product hunk with no Fieldwork notes, fixtures, workflows, or research files on the clean source branch.

## Target test convention decision

The canonical repository does not expose a separate Python unit-test namespace for `coverage.py`. Its declared ordinary suite is `make_mirror.sh` followed by `CMD=./mmdebstrap ./coverage.sh`, and `coverage.py` enforces that every non-dot entry under `tests/` has a matching `coverage.txt` stanza and is consumed as a shell-template scenario.

Therefore a guessed `tests/test_coverage_process_group.py` file would not be target-native: it would violate the suite inventory contract and be interpreted through the wrong runner. The clean source branch remains one file until an accepted regression location or harness integration is selected.

## Isolated target execution surface

CI machinery remains outside the clean product branch:

- runner branch: `linux-fieldwork/unit-11-coverage-backend-cancellation-runner`
- runner head: `f0319d53f515174c3794237f34f76699182ac509`
- runner parent/source head: `431614b3af58ba4f70791aa1d42cf5b71c965dd2`
- runner-only file: `.github/workflows/unit-11-coverage-backend-cancellation-runner.yml`
- internal controlled-fork review: `teamleaderleo/mmdebstrap#2`
- PR base: `linux-fieldwork/upstream-main-snapshot@77ec9be5417ee44c96343d2347145585da1b1f94`
- generated merge tested: `bf1f0cfde0ec6e0691c0dfb7d4656aafe3deab48`

The internal PR targets the exact canonical snapshot, not the unrelated Deepin packaging `master` branch and not the canonical upstream project.

## Exact target-repository gate

- workflow run: `30706007117`
- workflow run number: `3`
- result: success
- environment: Ubuntu 24.04.4, `ubuntu-24.04` runner image

### Candidate equivalence and null gate

- job: `91385135488`
- result: success
- exact base/source/candidate blob assertions: success
- zero-fuzz packet-patch application: success
- byte comparison between materialized patch result and target `coverage.py`: success
- target `coverage.py` compilation: success
- packet matrix first pass: 6/6 in 1.421 seconds
- packet matrix immediate rerun: 6/6 in 1.420 seconds
- source blob: `9a522484aef05deae514a98e4b6adf5feb6c886d`
- patch blob: `f1a2c75adfa009b6f1ac29e5a31bef526400444f`
- target candidate blob: `9e31f21cf37228257b5e0705d9ecb13b7a66e40f`
- candidate equivalence: success
- artifact: `8820336271`, `unit-11-target-null-gate`
- artifact size: 1440 bytes
- artifact SHA-256: `97eba28273b50dfcf51c32a2fe4cf49aa50da5634a3aaba6b052ad3728ae1ce8`
- expiry: 2026-10-30

### Refined topology gate

- job: `91385135449`
- result: success
- exact refined carrier and four test-blob assertions: success
- Python compilation: success
- first null/QEMU-wrapper/passwordless-sudo pass: 14/14 in 4.246 seconds
- immediate rerun: 14/14 in 4.367 seconds
- skips: none recorded
- actual passwordless-sudo controls executed
- refined QEMU test blob: `0c2a050faf8e98320fc0c4fe4634d46bdf7f0dfa`
- artifact: `8820337503`, `unit-11-target-refined-topology-gate`
- artifact size: 1590 bytes
- artifact SHA-256: `8d72b079fa9e30ee92bdf28cf217e9df3e4ae7a5ffeb7374b76950313bf24614`
- expiry: 2026-10-30

Both jobs uploaded their receipts and completed GitHub runner orphan-process cleanup. Node runtime deprecation warnings concerned the pinned GitHub actions and did not affect either gate result.

## Evidence relationship

The controlled target gate links all identities in one execution:

1. exact canonical base commit and source blob;
2. exact clean target source commit and candidate blob;
3. exact retained packet patch blob;
4. byte equality between patch-materialized and target-branch candidates;
5. focused baseline/status/group behavior twice;
6. refined null/QEMU-wrapper/passwordless-sudo behavior twice;
7. cleanup and immediate rerun.

Historical canonical Linux Fieldwork runs remain useful corroboration:

- run `30689911760`: zero-fuzz application and compilation twice; 6/6 packet controls twice; 14/14 refined controls twice; no skips; cleanup and immediate rerun success;
- run `30690101504`: both canonical jobs passed at the final packet head.

## Remaining blockers

- select an actual upstream-native regression integration rather than inventing a `tests/` entry;
- run the project-declared ordinary mirror-backed/source gate at clean target head `431614b3…`;
- review whether the isolated workflow and internal PR should be retained or retired after final evidence transfer;
- obtain eligible independent complete-diff acceptance for the clean target branch;
- refresh overlap and contribution-policy checks immediately before any public action;
- obtain explicit public-contact authority.

## Authority

No issue, pull request, merge request, review, email, or comment was created on the canonical upstream project. The controlled branches, internal PR, and runner are internal preparation only.
