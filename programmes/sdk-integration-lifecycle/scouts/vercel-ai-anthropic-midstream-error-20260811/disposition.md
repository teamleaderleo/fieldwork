## In simple words

This lane was superseded during overlap refresh and should not be delivered as a contribution.

The scout found a real classification asymmetry at `vercel/ai@7d40fafc394a2c9033f931eb85c895e3817f4b58`: Anthropic SSE errors appearing first are converted to `APICallError`, while equivalent valid errors later in the stream are emitted as raw provider objects. An owned, network-free reproduction was prepared in `teamleaderleo/ai#105`.

While the lane was being refined, the upstream AI SDK factory opened `vercel/ai#18671`, a broader implementation for issue #18669. That PR introduces public `StreamProviderError` normalization across AI SDK Core, including Anthropic-style overload classification, callback/stream identity tests, message-only payload handling, retry metadata, documentation, and runtime coverage. It subsumes the delivery value of this provider-local candidate.

## Disposition

- Fieldwork lane #860: closed `not planned` after overlap refresh.
- Owned reproduction #105: closed without delivery.
- Fieldwork report PR #861: preserve as negative/source evidence, then close.
- Do not race or contact the active upstream implementation.
- Automatic retry of a partially consumed stream remains a distinct question; typed-error normalization alone does not solve it.

Evidence labels: `source-read`, `upstream-documented`, `overlap-refreshed`.

No third-party upstream mutation or automated upstream contact was performed.