# Approaches — unit 24 Responses Lite first request after prewarm

## Decision

Selected: terminate the untraced warmup response chain only for the first generated Responses Lite request.

The selected boundary preserves all generic Responses WebSocket warmup compression, preserves Lite prewarm, preserves later generated-response continuation, and keeps the source change inside one request-selection hunk plus target-native tests.

## Decision criteria

1. The first generated Lite request carries the complete current logical input with no warmup predecessor.
2. Generic non-Lite warmup chaining remains unchanged.
3. Later Lite turns retain incremental reuse from a generated response.
4. A failed first generation retries the complete request.
5. No wire schema, public API, planner, or provider-capability change is introduced.
6. The source remains one clean commit and three files.

## Selected approach

### End Lite warmup response authority before first generation

Predicate:

```text
!warmup
&& model_info.use_responses_lite
&& websocket_session.last_response_from_untraced_warmup
```

Action:

- clear `last_response_rx`;
- return no incremental request and no untraced-warmup predecessor flag;
- use the existing full WebSocket request serializer.

Why this owns the transition:

- `ModelClientSession::stream_responses_websocket` has the current request, model mode, warmup state, connection state, response provenance, trace attempt, and request serializer in one place;
- the predicate expresses lifecycle provenance rather than comparing serialized bodies;
- the subsequent state assignment already resets warmup provenance after the generated request;
- later response reuse remains delegated to the existing generic incremental check.

Evidence:

- exact base `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`;
- exact head `9fd4ba575de8dd77bc411362256591ce9e7d8c82`;
- one commit, three files, `+301/-1`;
- historical exact source fence `3/3` and client controls `2/2`;
- complete-diff self-review attached to `teamleaderleo/codex#130`;
- fresh exact execution carrier `teamleaderleo/codex#135`.

Cost:

- the Lite input prefix is transmitted once during prewarm and once during first generation;
- later turns remain compressed.

## Public prior art that constrains the answer

### `openai/codex#23581` — logical trace after untraced warmup

This merged change intentionally keeps the generic compressed wire follow-up chained to the warmup response while recording the complete logical request for rollout replay.

Effect on unit 24: broad removal of warmup chaining is rejected. The selected predicate is explicitly Lite-only and leaves generic transport behavior intact.

### `openai/codex#27946` — Responses Lite tools as input items

This merged change moves Lite tools and instructions into input items. The complete input sequence therefore owns the Lite request identity rather than a separate top-level tools/instructions projection.

Effect on unit 24: it supplies the reason to send the complete first generated Lite request instead of relying on a `generate=false` setup parent.

### Earlier rollout-trace work `#22825` and `#23278`

These changes handled unresolved or omitted untraced warmup prefixes in trace/replay. They do not define the Responses Lite first-generation wire contract.

## Viable alternatives

### Compare serialized warmup and generated inputs

Design: construct both requests and permit warmup chaining only when a normalization rule proves the generated logical identity is safely represented by the warmup prefix plus delta.

Advantages:

- could support multiple future warmup contracts;
- might retain first-generation compression in a documented Lite subset.

Costs:

- request normalization must account for ordering, omitted/default fields, input-item identity, metadata, image preparation, and future schema evolution;
- widens the patch and creates a second compatibility algorithm beside existing incremental comparison.

Reopening trigger: maintainers document a valid Lite first-generation chaining contract with an exact equivalence rule.

### Add an explicit response-provenance state enum

Design: replace the boolean plus response receiver combination with typed states such as `None`, `Warmup`, and `Generated`.

Advantages:

- stronger state-machine readability;
- can prevent impossible provenance combinations.

Costs:

- larger refactor across connection reset, response completion, tracing, retries, and tests;
- unnecessary for the single transition while the existing fields already encode the required facts.

Reopening trigger: another defect demonstrates that response provenance remains ambiguous after this correction.

### Send the complete request but keep the warmup response ID

Design: include both `previous_response_id = warm-1` and the complete input.

Why rejected:

- preserves setup response authority despite the full payload;
- creates an ambiguous ownership model and unmeasured provider behavior;
- does not satisfy the governing invariant that only a generated response becomes the predecessor of later generated turns.

### Reset the whole WebSocket session

Design: reconnect before first generation.

Why rejected:

- loses the connection benefit of prewarm;
- changes handshake, authentication, and retry behavior;
- broader than clearing one response-chain receiver.

### Disable Lite prewarm

Why rejected:

- removes the latency optimization rather than correcting response ownership;
- changes scheduling and startup behavior outside the unit.

### Treat a larger Tokio worker stack as the product repair

Why rejected:

- stack size changes the test environment, not request identity;
- both isolated client controls pass without using stack size as product logic;
- the default-versus-16-MiB result remains a test-harness classifier only.

### Fold in planner, Code Mode, or tool-catalogue work

Why rejected:

- those areas decide which tools enter the Lite catalogue;
- unit 24 decides whether the first generated request inherits setup response authority;
- the current source fence excludes all planner and tool-registration files.

## Executed history

| Date | Source / carrier | Result | Decision |
| --- | --- | --- | --- |
| 2026-07-30 | broad owned carrier `teamleaderleo/codex#23` | useful reproduction; source far too broad | isolate a three-file candidate |
| 2026-07-30 | source `e520da008366cd720ef58fa0b489efc0a2867e97`; carrier `40a56eefce26ea647a65779faeb783d65a84a49a` | source fence `3/3`; client controls `2/2`; agent `default:101;large:0` | retain bounded implementation and stack discriminator |
| 2026-08-01 | source `2c3f21d38056d2d77215cd9dce820a680d11cfe8` on parent `670f69416bf91c5dfd8b58669e78050b584ff053` | clean one-commit currentization; ordinary CI included unrelated repository failures | continue instead of stopping at repository-wide failures |
| 2026-08-01 | source `9fd4ba575de8dd77bc411362256591ce9e7d8c82` on parent `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff` | five-commit public drift was file-disjoint; complete self-review found no source blocker | run exact current-head execution and synchronize packet |

## Current execution plan

Execution-only PR `teamleaderleo/codex#135` runs, on the immutable source head:

1. exact three-file source fence;
2. `cargo fmt --all -- --check`;
3. both exact client controls;
4. full-agent control at default and 16-MiB worker stacks;
5. `just test -p codex-core` at a 32-MiB worker stack;
6. `just fix -p codex-core`;
7. clean-worktree and diff checks.

The execution workflow is excluded from the canonical source diff and will be closed and removed from its branch after the receipt is transferred.
