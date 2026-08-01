# Unit 13 approaches ledger

## In simple words

The selected product repair gives each backend invocation one caller-owned session/process group and sends cancellation to that group. Wrapper-only termination loses because nested work survives. Stronger escalation remains deferred because only synthetic evidence supports it.

Canonical current-source packaging and execution now live on Linux Fieldwork PR #401. Historical PRs #313 and #339 are closed with evidence transferred. PR #406 is closed as a duplicate ancestry restack.

## Selected product approach

### Caller-owned session/process group

```python
proc = subprocess.Popen(argv, start_new_session=True)
...
os.killpg(proc.pid, signal.SIGTERM)
proc.wait()
raise SystemExit(130)
```

Why it wins:

- `coverage.py` selects the backend and can establish the operation boundary before backend code runs;
- one backend-agnostic boundary covers null, QEMU-wrapper, sudo, and future in-group descendants;
- parent-only SIGINT reaches nested in-group work;
- ordinary unsignaled behavior stays unchanged in executed controls;
- no backend-specific process discovery or escalation policy is added.

Retained upstream-root patch blob: `f1a2c75adfa009b6f1ac29e5a31bef526400444f`.

## Selected packaging approach

### Canonical unit packet plus future controlled-fork branch

Current durable packet:

- PR [#401](https://github.com/teamleaderleo/linux-fieldwork/pull/401)
- branch/head `upstream/unit-11-coverage-backend-cancellation@d232e4fdd67cf0592e129a60534e984dcbec6bfe`
- canonical upstream base `77ec9be5417ee44c96343d2347145585da1b1f94`
- current-source execution runs `30689911760` and `30690101504`

Why it wins:

- retains one upstream-root product patch;
- records exact canonical source and wrapper blobs;
- executes the selected patch and refined topology controls on canonical source;
- keeps issue, PR draft, decisions, source map, tests, artifacts, and handoff together;
- transfers unique evidence from historical carriers;
- avoids treating an internal research branch as the eventual public source branch.

Future delivery still requires a controlled canonical fork and clean candidate branch.

## Executed losing approaches

### Imported wrapper-only termination

```python
proc = subprocess.Popen(argv)
...
proc.terminate()
proc.wait()
break
```

Result: immediate wrapper receives TERM; nested work remains able to perform later work. The driver can also return status 0.

### Status-only repair

Behavior: retain wrapper-only TERM, diagnose, and exit 130.

Result: status becomes accurate while nested work survives. This proves status correctness and operation cancellation are separate requirements.

Historical records: issue #141; PRs #143 and #204.

### Reuse historical CI as current-source evidence

Rejected. Historical CI 931/943 remains valid for exact historical source/base pairs. Canonical current-source execution was required and is now supplied by PR #401.

### Byte-identical Linux Fieldwork ancestry restack

PR #406 copied the exact nine PR #313 blobs onto current Linux Fieldwork `main` at `e82b9b059850fce1efcf8daadef89049495a8b27`.

Result: useful ancestry confirmation, but weaker than PR #401, which applies the upstream-root patch to canonical mmdebstrap source and executes both focused matrices. PR #406 is closed as superseded.

### Keep historical carriers open

Rejected after evidence transfer. PR #313's unique mechanism history and PR #339's refined QEMU evidence are retained by PR #401 with exact identities and canonical reruns. Both historical PRs are closed without merge to reduce duplicate ownership.

### Treat Salsa packaging VCS as canonical contribution destination

Rejected after current project packet review. Canonical contribution destination is Forgejo `josch/mmdebstrap` on `main`. Salsa remains Debian packaging context.

### Backend-specific descendant discovery

Rejected because the caller would need to understand evolving shell, pipeline, QEMU, sudo, and future backend topologies. Creating one group before launch is smaller and more stable.

### Same-session background process group

Rejected after the retained PTY comparison: background process groups can stop on terminal input. A new session preserved inherited descriptor I/O in the reduced control while removing controlling-terminal association.

### Claim arbitrary group quiescence

Rejected. `proc.wait()` waits for the immediate wrapper only. Claims remain limited to complete settlement in executed TERM-responsive topologies.

### TERM-to-KILL escalation

Compared in issue #341 and closed PR #347 at `615bd4f5256d9851f682e48e037169ceeb7bb98c`.

Synthetic controls found bounded TERM-to-KILL drained the resistant test group and retained final status. It remains unselected because no real backend showed need, no proportional grace interval was justified, and KILL can discard cleanup state.

Reopening trigger: a real backend ignores/materially defers TERM, outlives its wrapper, or demonstrates an operational repeated-SIGINT requirement.

## Packet fixture approach

### Exact original harness

Preserved as `fixtures/local-process-model/harness_original.py` because it is the source of the first packet-time run.

It loses as the default replay because it requires `/tmp/unit13-probe`, waits for only one readiness marker, and has weaker failure cleanup.

### Reviewed relocatable harness

Selected as `fixtures/local-process-model/harness.py` because it resolves sibling files, waits for both markers, detects early exit, and cleans all modeled PIDs in `finally`.

Compilation and execution pass with unchanged output. This affects packet replay only.

## Carrier history

- PR #204 — merged internal status-only comparator;
- PR #313 — closed, superseded for delivery; historical mechanism/evidence head `dfc6d050…`;
- PR #332 — closed byte-identical patch-context repair;
- PR #336 — closed divergent QEMU evidence repair;
- PR #339 — closed with refined evidence transferred;
- PR #347/#353 — closed stronger-policy research;
- PR #401 — active canonical current-source packet;
- PR #406 — closed duplicate ancestry restack.

## Adjacent questions excluded

- repeated SIGINT during cleanup;
- TERM-resistant or TERM-deferring descendants;
- bounded group-drain diagnostics and escalation;
- descendants that create another group/session;
- full interactive QEMU/debvm and direct `/dev/tty` behavior;
- prepared mirrors, package operations, and non-Linux execution.

These stay outside unit 13 unless real target evidence makes one a prerequisite.
