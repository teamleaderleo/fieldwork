## In simple words

fd documents repeated `--exec-batch` commands as running in the order they were given. Exact current batch execution can violate that order because every declared command owns an independent command builder and each builder can execute as soon as its own argv capacity is exhausted.

This is target-executed through both the private batch owner and the real public `fd` command on exact source `ee20f426ddf338ac7ead5c5f00ea49258005caaf`.

The discriminator is clean:

```text
equal command capacity       -> 1,2
only later command pressured -> 2,1,2
```

The real CLI reproduces the same inversion over 10,208 files. This experiment is promoted to Fieldwork candidate #832.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Worker: `GPT-5.6 Sol`
- Experiment: `EXP-20260811-fd-exec-batch-order`
- Candidate owner: #832
- Target: `sharkdp/fd@ee20f426ddf338ac7ead5c5f00ea49258005caaf`
- Related upstream report: [#2033](https://redirect.github.com/sharkdp/fd/issues/2033)
- Claim scope: mechanism + public CLI consequence
- Evidence class: `target-executed`
- Final run: `31443852287`
- Final job: `93633857964`
- Upstream contact authorized/performed: `false` / `false`

## Source map

`CommandSet::execute_batch()` creates one `CommandBuilder` per declared batch command.

For every discovered path it loops through builders in declaration order and calls `builder.push(path, ...)`.

Each `CommandBuilder::push()` independently checks:

1. configured batch count;
2. whether its own current command can accept the next generated path plus trailing arguments.

If either limit is reached, `push()` calls `finish()` immediately. `finish()` synchronously executes that builder's current command and resets only that builder.

The final declaration-order loop only applies to builders still buffered at end-of-input. It cannot undo an earlier independent flush from a later command.

## Target execution: owner

The injected tests use harmless `/bin/sh -c` commands that append command IDs to one temporary log.

### Equal-capacity control

Two builders receive the same path arguments and remain under capacity until explicit finalization.

Observed:

```text
1
2
```

Result: declaration order preserved.

### Asymmetric-capacity discriminator

After one common path, only builder 2 is padded with harmless fixed arguments. Every filler insertion is preflighted through fd's own `argmax::Command::args_would_fit()` so the test adapts to the actual runner limit.

Before the second path:

- command 1 still reports that the path fits;
- command 2 reports that the same path does not fit.

Command 1 receives the path and stays buffered. Command 2 then receives the path, immediately flushes its existing batch, and writes:

```text
2
```

while command 1 has still never run.

After explicit finalization, the complete log is:

```text
2
1
2
```

Result: target owner crosses declaration order.

## Target execution: public CLI

The same workflow builds exact `fd` and creates a temporary search tree sized from the runner's actual `SC_ARG_MAX`.

Receipt:

```text
ARG_MAX:              4194304
files:                10208
path bytes:           2307008
later-command filler: 511 args / 2093567 bytes
```

Both repeated `-X` commands simply append their command ID to a temporary log. Search traversal uses one thread.

### Equal-size CLI control

Neither repeated command carries extra fixed argv.

Observed:

```text
FIELDWORK_CONTROL exec-batch-order= ['1', '2']
```

### Asymmetric CLI discriminator

Only the second declared `-X` command carries the fixed filler arguments.

Observed:

```text
FIELDWORK_RESULT exec-batch-order= ['2', '1', '2']
FIELDWORK_RESULT public-cli-later-command-executed-first
```

The `fd` process exits successfully. The later declared command executes first solely because its child-command argv ceiling is reached before the earlier builder's ceiling.

Machine-readable receipt: `result.json`.

## Promotion

Candidate owner: Fieldwork #832.

A repair belongs at the multi-command scheduling owner rather than inside one builder. A promising family is a shared batch barrier:

1. preflight the next generated path against all declared batch builders;
2. if any builder must flush because of count or argv capacity, finish every non-empty builder in declaration order;
3. then add that path to fresh builders.

That aligns batch boundaries to the tightest declared command and prevents a later builder from independently crossing the documented order.

Regression work should compare:

- equal-capacity repeated commands;
- asymmetric fixed argv;
- explicit `--batch-size` boundaries;
- single-command batch behavior;
- exit/error propagation across repeated commands.

## Validation correction

The first playground/context validation generation rejected the metadata label `Reported`; Fieldwork accepts `Observed` for issue-report evidence. This was a metadata-only validation failure and had no relationship to fd execution. The promoted metadata uses the accepted evidence label.

## Stop condition

Experiment complete and promoted. Continue source work only in an owned fd fork or a Fieldwork candidate carrier. Refresh fd head and overlap before any external proposal. External issue, pull-request, comment, review, or other upstream interaction remains manual human work.