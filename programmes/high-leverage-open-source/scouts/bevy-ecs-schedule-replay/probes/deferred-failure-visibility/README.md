# Deferred failure visibility probe

This crate characterizes whether commands queued before a Bevy system failure become visible under the single-threaded and multithreaded schedule executors.

## Exact source

Check out Bevy development source at:

`25368b78ce5e9b15dc770cdf2af4595602cc8a7b`

into the Fieldwork repository path:

`.fieldwork/bevy`

Then run:

```bash
cargo test --manifest-path programmes/high-leverage-open-source/scouts/bevy-ecs-schedule-replay/probes/deferred-failure-visibility/Cargo.toml
cargo run --manifest-path programmes/high-leverage-open-source/scouts/bevy-ecs-schedule-replay/probes/deferred-failure-visibility/Cargo.toml
```

## Matrix

The probe distinguishes:

- successful system completion;
- returned ignored error;
- returned panic-severity error under the default handler;
- system panic under a custom returning handler;
- system panic under the default handler.

Every case runs under both built-in executors. The assertions encode the development-source prediction recorded in the parent report. They characterize current behavior and do not select apply-versus-discard policy.

## Boundary

No network, renderer, asset server, application plugin, or external process is required after the exact source checkout exists. A toolchain or dependency failure is harness evidence, not a Bevy result.
