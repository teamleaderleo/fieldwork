# Result notes

Run date: 2026-08-01  
Command: `python3 run.py --output results/latest.json`  
Repeat count: 2  
External network: none; the runner uses only a refused loopback connection to `127.0.0.1:1`.

## Observed results

Both runs produced the same distinguishing values:

| Case | Before | After | Other observation |
| --- | ---: | ---: | --- |
| destination symlink target | 16 bytes | 0 bytes | destination path changed from symlink to a 111-byte regular HSTS file |
| existing HSTS cache under `RLIMIT_FSIZE=1024` | 10,801 bytes | 1,024 bytes | curl returned transfer status 7 and stderr contained only the refused connection, not a separate write error |

## Interpretation

The installed curl 8.10.1 reproduces both reported persistence mechanisms:

1. opening the final HSTS path follows and truncates a symlink target before the destination path is replaced;
2. a later file-size failure does not preserve the previous complete cache as an all-or-nothing transaction.

The current upstream source at `527573490eb2564b3d7c9dd51d8bff963b5d6303` still contains the same open-before-`fstat` control flow, but this experiment did not build or execute that exact revision. Current-master execution remains a separate follow-up.

The `RLIMIT_FSIZE` result proves loss of the previous complete cache. It does not isolate whether the final 1,024-byte file came from the initial destination truncation, partial temp output followed by rename, or both. A direct `Curl_fopen()` harness with deterministic fault injection is required to separate those lifecycle stages.

## Cleanup

All mutable files lived below `TemporaryDirectory`. The runner retained no cache files, sockets, processes, or external state after completion.
