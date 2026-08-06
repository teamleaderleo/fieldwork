# Upstream issue — submitted

Live issue: [open-telemetry/opentelemetry-js#6977](https://redirect.github.com/open-telemetry/opentelemetry-js/issues/6977)

Title: `Lifecycle fanout can skip processors present at operation start`  
State at refresh: `open`  
Filed: `2026-08-05`  
Linked pull request: [open-telemetry/opentelemetry-js#6980](https://redirect.github.com/open-telemetry/opentelemetry-js/pull/6980)

The live issue is the source of truth. This file previously held the pre-submission draft; git history preserves that text.

The submitted report covers:

- direct lifecycle throws that skip later processors;
- opening-set mutation during fanout;
- stale `TracerProvider.forceFlush()` timers;
- the trace and logs lifecycle requirements;
- a runnable public-interface reproduction;
- the proposed snapshot-and-adapter repair.

Technical investigation: [`DEEP_DIVE.md`](./DEEP_DIVE.md)
