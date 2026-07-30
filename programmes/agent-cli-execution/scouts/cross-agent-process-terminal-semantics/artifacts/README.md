# Process and terminal semantics case pack

## In simple words

This runner creates small child processes whose behavior is easy to recognize: they alternate stdout and stderr, detect whether they have a terminal, rewrite a line, leave a pipe open in a descendant, emit invalid UTF-8, print a final marker, or require process-group cancellation. It does not invoke either target CLI. Target-specific adapters can run the same children and compare their own events and final results.

## Run

```bash
python3 run_process_terminal_cases.py --pretty > results.json
```

The runner uses the Python standard library. Two process-tree cases invoke `bash`. The current retained result was produced on Linux with Python 3.13.5 and no network access.

## What the model preserves

The cases preserve transport identity, channel identity, observed chunk order, direct process exit, output EOF, terminal dimensions, raw control bytes, invalid UTF-8, and process-group cancellation. They omit approvals, sandboxes, model behavior, UI rendering code, remote execution, and application shutdown.

`case-pack.json` defines the reusable questions and invariants. `results-linux-python-3.13.5.json` is a neutral baseline rather than an expected target result.
