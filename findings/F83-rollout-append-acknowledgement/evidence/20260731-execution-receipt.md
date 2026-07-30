# Execution receipt — rollout append acknowledgement

Canonical source: `teamleaderleo/codex#84@d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`  
Execution carrier: `teamleaderleo/codex#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc`  
Workflow run: `30583967538`  
Evidence class: `target-executed`  
Upstream contact authorized: `no`

## Executed source contract

- exact source base `a01a2d91461a57809e944de7758477b92617ab01`;
- exact three-file source fence;
- formatting and diff hygiene;
- four uniquely resolved full test names executed with `--exact`;
- complete `codex-thread-store` package;
- source-only publication after every required gate passed.

## Exact controls

- `append_outcome_ephemeral_history_is_authoritative`;
- `append_outcome_reports_successful_live_append`;
- `append_outcome_reports_prewrite_failure`;
- `append_outcome_reports_commit_then_error_as_failure`.

Retained marker: `FIELDWORK_APPEND_OUTCOME_EXACT=4/4`.

## Established result

The session boundary can expose the durable append acknowledgement while preserving existing live-history and raw-item publication ordering. The fixture distinguishes error-before-write from error-after-write.

## Evidence limit

The receipt establishes the bounded in-memory thread-store paths and the named package gate at one exact source revision. It supplies no typed persistence state, retry authority, replay result, remote-effect certainty, or cross-backend transaction guarantee.
