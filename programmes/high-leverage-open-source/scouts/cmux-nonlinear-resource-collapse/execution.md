# cmux nonlinear resource-collapse execution log

## In simple words

The source findings now have an owned-fork execution surface. The fork branch starts exactly from the pinned upstream revision, contains investigation-only code, and has GitHub Actions jobs queued for the journal model and macOS RPC write-admission test.

This file records executed state separately from the scout's source analysis so a prepared probe never gets mistaken for a measured result.

## Fork state

Owned repository: `teamleaderleo/cmux`  
Branch: `fieldwork/nonlinear-resource-collapse`  
Base / merge base: `8ef183f1e5de765b183aec9d1799f17a0848ae84`  
Current recorded branch head: `f9e461731f6ff3ea60f1a505ab4fbeea954e983b`  
Ahead of pinned upstream: 5 commits  
Behind pinned upstream: 0 commits

Files added by the experiment:

- `.github/workflows/fieldwork-nonlinear-resource-collapse.yml`
- `Packages/macOS/CmuxRemoteDaemon/Tests/CmuxRemoteDaemonTests/RemoteDaemonRPCClientWriteAdmissionScalingTests.swift`
- `scripts/fieldwork/cmux-resource-collapse/journal_backlog_model.py`
- `scripts/fieldwork/cmux-resource-collapse/macos_process_sampler.sh`
- `scripts/fieldwork/cmux-resource-collapse/README.md`

No production source file has been changed at this stage.

## Probe intent

### macOS RPC write-admission scaling

The new Swift suite uses the package's existing `transportExecutableOverride` test seam.

Control:

- fake helper continually reads and responds;
- 200 concurrent RPC callers;
- all callers must settle;
- zero failures expected.

Candidate failure:

- fake helper answers startup `hello`;
- helper remains alive for two seconds while refusing later stdin bytes;
- a direct 4 MiB physical write occupies the actual `RemoteDaemonRPCClient.writeQueue` and blocks in `FileHandle.write`;
- bursts of 1, 10, 50, and 200 later RPC calls use a 50 ms response timeout;
- desired bounded behavior requires them to settle within 750 ms;
- current source ordering predicts red because callers register before `writeQueue.sync` and only begin `waitForCall` after the physical write returns;
- the helper's finite lifetime is a safety breaker so an expected red result cleans itself up.

This is deliberately a desired-invariant assertion, not a characterization test that encodes the bug as success.

### Journal model

The Python probe parses its limits directly from the checked-out `journal_forwarder.rs`, then evaluates the 1 / 10 / 50 / 128 / 200 producer sequence under a 60 second outage. It refuses unexpected constant syntax instead of silently using hard-coded values.

The model remains labelled illustrative. Its purpose is to pin the queue arithmetic and discovery-cap plateau while a runtime producer harness is developed.

### Process sampler

The macOS sampler writes CSV rows containing epoch time, RSS, thread count, descriptor count, IPv4/IPv6 sockets, Unix sockets, direct children, and recursive descendants. It is intended for the runtime phase after the first red/green owner is established.

## GitHub Actions

Workflow: `Fieldwork nonlinear resource collapse`

Run 1: https://github.com/teamleaderleo/cmux/actions/runs/33551061330  
Head: `ea0338c56b9bab22b8a37e794ed34ecbca907deb`  
State when recorded: queued

Run 2: https://github.com/teamleaderleo/cmux/actions/runs/33551141842  
Head: `f9e461731f6ff3ea60f1a505ab4fbeea954e983b`  
State when recorded: queued

Jobs on each run:

- `journal-model` — Linux source-pinned arithmetic/model check
- `macos-rpc-write-admission` — macOS Swift package test

The latest run is the authoritative one because it includes the README commit in addition to the executable probe commits. Run 1 may still be useful as an earlier execution receipt but should not replace the latest-head result.

## Evidence labels at this point

- Fork branch existence and exact base: **Executed / Observed**.
- Fork diff contains investigation-only files: **Observed**.
- Workflow accepted and jobs queued: **Executed / Observed**.
- Journal model numerical output: **Unknown** until a job or local run completes.
- Responsive 200-caller Swift control: **Unknown** until macOS execution completes.
- Stalled 1/10/50/200 Swift cases: **Unknown** until macOS execution completes.
- Production fix efficacy: **Unknown** because no production fix exists yet.

## Next decision

Wait for the latest-head verifier outcome only in the sense of dependency ordering: production code should follow executed evidence. The current work unit remains active in this conversation, and the next edit will be selected from actual job output rather than by assuming the red test behaves as predicted.

Upstream remains read-only. Upstream contact authorization remains `false`.
