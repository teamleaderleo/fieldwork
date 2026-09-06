# Local timing check

## In simple words

This historical measurement asks whether the additional configuration copies produce a visible local slowdown. Two small in-memory scenarios showed overlapping timing ranges. It does not establish full-startup performance or memory cost; its role is supporting evidence for the adjacent study guide.

Compared upstream parent `8492422b8f110625a90c702f42f30784e8cf19dc` with candidate `4bfb19a34fabb33a2ae414362ca8f2d41d7b3959` on macOS, Node 26.8.1. At measurement time, the local uncommitted changes only trimmed tests. The later submitted commit `9641e4f018ed1a2917d617832ff69560c86d0ef9` has the same production code.

## Resolver timing

Both versions used built Vite bundles. Each sample ran in a separate Node process, warmed up with 60 resolutions, requested garbage collection before the measured batch, and timed 200 resolutions. Five samples per version and scenario alternated version order. Each resolution received fresh mutable input so baseline accumulation would not distort the comparison. Both versions used the same temporary project root, with config-file and env-file loading disabled.

| Scenario | Baseline median batch-average ms/resolve | Candidate median batch-average ms/resolve |
| --- | ---: | ---: |
| Minimal config | 0.3342 | 0.3345 |
| Config exercising optimizer conversion, environments, HMR, host/path arrays, and CSS defaults | 0.3399 | 0.3390 |

Ranges overlap for both scenarios. No meaningful slowdown was observed in this bounded check. This does not measure full startup, real config-file loading, downstream integrations, retained heap, or worst-case large configuration objects. Differences should not be interpreted as a speedup.

Raw results: [resolve-timing.json](resolve-timing.json). Per-process harness: [resolve-timing.mjs](resolve-timing.mjs); arguments are the built Vite entry point, a temporary root directory, and either `minimal` or `configured`. The disposable baseline worktree and temporary root were removed after measurement.

## Test timing

The focused correctness run retained during test trimming passed 135 tests across the three relevant files. Of those, 22 are added by the trimmed patch: five additions to `config.spec.ts`, sixteen inline-config cases, and one real restart/cache case.

Reported test-body durations for those additions summed to about 92 ms: 3 ms for the five existing-file additions, 39 ms for inline-config cases, and 50 ms for restart/cache. This excludes test-runner startup and module loading; it is not a measurement of incremental whole-suite wall time. An earlier full-suite run reported about 205 ms for the then-untrimmed inline-config file and 152 ms for restart, demonstrating that these timings vary with execution conditions.

The test cost is small in these local observations. Correctness coverage, rather than runtime savings, motivated trimming overlapping cases.
