# cmux journal backlog model result

## In simple words

The source-pinned journal backlog model executed successfully on the owned fork. This is still model evidence rather than measured process memory, but the job proves the calculation is using the exact constants in the checked-out target source instead of stale numbers copied into the notes.

## Execution receipt

Owned fork: `teamleaderleo/cmux`  
Branch: `fieldwork/nonlinear-resource-collapse`  
Workflow run: https://github.com/teamleaderleo/cmux/actions/runs/33551622521  
Job: `journal-model`  
Job conclusion: `success`  
Checked-out head: `89478a635f6db441f1727002c6751c23b75c2d61`  
Target ancestry base: `8ef183f1e5de765b183aec9d1799f17a0848ae84`

The job read these values from `cmux-tui/crates/chatmux-relay/src/journal_forwarder.rs`:

- `MAX_BATCH_RECORDS = 100`
- `MAX_BATCH_BODY_BYTES = 4,194,304`
- `MAX_DISCOVERED_SESSIONS = 128`
- `DEFAULT_REQUEST_TIMEOUT = 30 seconds`
- `DEFAULT_MAX_BACKOFF = 60 seconds`

## Default modeled sequence

Inputs:

- 10 records/s per active session
- 2,048 encoded bytes per record
- 60 second POST outage
- one 100-record batch already owned by the in-flight POST

Executed output:

| Requested sessions | Active sessions | Aggregate records/s | Pending records after outage | Encoded pending MiB |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 10 | 500 | 0.98 |
| 10 | 10 | 100 | 5,900 | 11.52 |
| 50 | 50 | 500 | 29,900 | 58.40 |
| 128 | 128 | 1,280 | 76,700 | 149.80 |
| 200 | 128 | 1,280 | 76,700 | 149.80 |

The 128/200 plateau is an important discriminator: discovery bounds the number of producer workers, while it does not bound retained records per active worker during a blocked shared POST.

## Interpretation

This job establishes the arithmetic and exact source constants. It does not establish real RSS, allocator overhead, socket buffering, or the runtime point where the process becomes unhealthy.

The runtime harness in the same branch is intended to supply those measurements using the actual `journal_forwarder::start` path with fake cmux-tui Unix sockets and local healthy/stalled HTTP endpoints.

Evidence label: **Executed model / Illustrative resource size**.

Upstream remains read-only. Upstream contact authorization remains `false`.
