## In simple words

fd documents repeated `--exec-batch` commands as running in the order they were given. Current batch execution keeps a separate command builder for every declared command, and each builder can execute independently when its own command line reaches the OS argv limit.

That creates a direct ordering hazard: command 2 can flush and execute while command 1 is still buffering the same search results.

This experiment isolates that owner without requiring a huge real directory tree. It builds exact current fd source and injects test-only controls inside `src/exec/mod.rs`, where private `CommandBuilder` state is visible.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Worker: `GPT-5.6 Sol`
- Experiment: `EXP-20260811-fd-exec-batch-order`
- Target: `sharkdp/fd@ee20f426ddf338ac7ead5c5f00ea49258005caaf`
- Related upstream report: [#2033](https://redirect.github.com/sharkdp/fd/issues/2033)
- Claim scope: mechanism
- Evidence class: `source-read`, pending `target-executed`
- Upstream contact authorized/performed: `false` / `false`

## Source map

`CommandSet::execute_batch()` creates one `CommandBuilder` per declared command.

For every discovered path it loops through the builders in declaration order and calls `builder.push(path, ...)`.

Each `CommandBuilder::push()` independently checks:

1. configured batch count;
2. whether its own command line can accept the next generated path plus trailing arguments.

If either limit is reached, `push()` calls `finish()` immediately. `finish()` executes that builder's current command before resetting it.

The final loop only restores declaration ordering for builders that remain buffered until end-of-input. It cannot undo an earlier independent flush.

## Target discriminator

The injected tests use harmless `/bin/sh -c` commands that append command IDs to one temporary log.

### Equal-capacity control

Two builders receive the same two path arguments and remain below their argv ceilings. Neither command executes during `push()`. Finalization runs builder 1 then builder 2.

Expected log:

```text
1
2
```

### Asymmetric-capacity discriminator

Both builders receive one initial path. Then only builder 2 is padded with harmless fixed arguments until the same second path no longer fits its current command line, while builder 1 still has ample capacity.

Execution sequence:

1. builder 1 accepts path 2 and remains buffered;
2. builder 2 sees path 2 does not fit;
3. builder 2 calls `finish()` immediately and writes `2` to the log;
4. only later does finalization execute builder 1.

Expected first log entry before finalization:

```text
2
```

Expected final log prefix:

```text
2
1
```

A final second `2` is expected because builder 2 starts a fresh batch with path 2 after its early flush.

## Why the probe is bounded

The test asks `argmax` itself whether arguments fit and pads only while each added filler argument remains accepted. It therefore adapts to the runner's actual argv ceiling instead of hardcoding Linux ARG_MAX.

No external commands have side effects beyond writing marker lines into a temporary directory.

## Stop condition

If equal-capacity execution stays `1,2` and asymmetric capacity produces `2` before builder 1 executes, promote the mechanism into a public-CLI reproduction plan. If both cases remain declaration-ordered, stop and remap the missing barrier.

External fd remains read-only. No upstream interaction is authorized.