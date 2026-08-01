# Controlled target branch receipt — 2026-08-01

## Result

The controlled mmdebstrap repository is now accessible and the clean source candidate has been materialized directly from the exact canonical commit already used by the retained current-source gates.

This clears the former `NEEDS FORK` / missing-source-branch blocker. It does not clear target execution, upstream-native regression, ordinary-gate, or public-authority blockers.

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

## Isolated runner branch

A separate branch preserves CI machinery outside the clean product diff:

- runner branch: `linux-fieldwork/unit-11-coverage-backend-cancellation-runner`
- runner head: `f60b9888f54e51e5fc6b109ec6c24f9127ab6d4a`
- runner parent/source head: `431614b3af58ba4f70791aa1d42cf5b71c965dd2`
- added file: `.github/workflows/unit-11-coverage-backend-cancellation-runner.yml`

The workflow is designed to:

1. assert the exact base, source commit, base blob, and candidate blob;
2. apply packet patch blob `f1a2c75adfa009b6f1ac29e5a31bef526400444f` with zero fuzz to the exact base;
3. require byte equality between that materialized candidate and target `coverage.py`;
4. compile the target candidate;
5. run the six-control packet matrix twice;
6. run the refined 14-control null/QEMU-wrapper/passwordless-sudo matrix twice;
7. upload exact identity and log artifacts.

No workflow run, check, or commit status surfaced after the runner push. Classification: runner trigger/enabling blocker. This is not classified as a candidate failure because no job started.

## Evidence relationship

The candidate hunk and source base remain covered by the canonical Linux Fieldwork executions:

- run `30689911760`: zero-fuzz application and compilation twice; 6/6 packet controls twice; 14/14 refined controls twice; no skips; cleanup and immediate rerun success;
- run `30690101504`: both canonical jobs passed at the final packet head.

Those runs validate the exact base plus retained patch. The controlled target branch now preserves the matching source commit and candidate blob. A target-repository run is still required by the stricter `teamleaderleo/fieldwork#435` completion contract.

## Remaining blockers

- enable or otherwise trigger the isolated target runner, or execute an equivalent exact-head target gate;
- select an actual upstream-native regression integration rather than inventing a `tests/` entry;
- run the project-declared ordinary mirror-backed/source gate at the target head;
- review whether the isolated workflow should be retained or retired after execution;
- obtain eligible independent complete-diff acceptance for the clean target branch;
- refresh overlap and contribution-policy checks immediately before any public action;
- obtain explicit public-contact authority.

## Authority

No issue, pull request, merge request, review, email, or comment was created on the canonical upstream project. The controlled branch and runner are internal preparation only.
