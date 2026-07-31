# Fieldwork Assistance Receipt

## In simple words

Use this receipt when one worker helps work owned by another worker, especially when both appear under the same GitHub account. It records who helped, which exact generation they observed, what they produced, and whether ownership changed. Assistance never transfers a writer lease by implication.

This file is a **normative fail-closed template contract**. Its blocks and locator forms are reviewable conventions. They are not yet a mechanically enforced event format. A later parser or router must separately prove grammar validation, linkage, uniqueness, currentness, and transfer-record verification before claiming deterministic enforcement.

## Stable identity and qualified locators

The stable event key is the composite:

```text
(<owning repository>, <owning issue number>, <Assistance ID>)
```

An Assistance ID alone is not globally unique. Use one stable public-safe ID within the owning issue, for example:

```text
assist:<UTC date>:<short random or assignment id>
worker:<role>:<UTC date>:<short random or assignment id>
```

Assistance and worker identifiers must be 1–160 ASCII characters, begin with the appropriate `assist:` or `worker:` prefix, and otherwise contain only lowercase letters, digits, `.`, `_`, `:`, or `-`. Whitespace, control characters, Unicode confusables, path separators, query fragments, and line breaks are invalid.

Identifiers must not contain credentials, tokens, private chat or session identifiers, personal data, hostnames, filesystem paths, provider request IDs, or private infrastructure details. They are attribution and correlation metadata, not authentication, write authority, or proof of independent-review eligibility.

Every durable locator must be repository-qualified. Use forms equivalent to:

```text
owner/repo#issue-<number>-comment-<id>
owner/repo@<commit-sha>
owner/repo#pr-<number>@<head-sha>
owner/repo/actions/runs/<run-id>/artifacts/<artifact-id>@sha256:<digest>
owner/repo#issue-<number>:lease-comment-<id>
```

A bare numeric comment, artifact, issue, pull-request, or run ID is ambiguous and invalid for current routing.

The same composite event key appears throughout one claim, completion, and supersession chain. A legacy reconciliation starts a new chain with a fresh composite key. Never recycle a composite key for another bounded question or target generation.

## Identity and ownership fields

- Owning repository:
- Owning issue number:
- Assistance ID:
- Assistance state: `claimed | complete | superseded | legacy-reconciled`
- Authoritative claim receipt: exact repository-qualified owning-issue comment; required for `complete` and `superseded`, `not applicable` while `claimed`; a `legacy-reconciled` event uses its exact legacy locators instead
- Optional claim mirrors: exact qualified commit or artifact locators, or `none`
- Helper worker instance:
- Owner worker instance: `unknown` when the earlier record did not preserve one
- Target artifact or branch:
- Exact observed input generation:
- Target generation at completion or supersession: `not applicable` while state is `claimed`
- Input currentness: `exact | moved | unknown | not applicable`
- Currentness observed at: exact timestamp or `not applicable`
- Currentness observation source: exact qualified source or `not applicable`
- Assistance type: `review | reproduction | regression | repair-stack | evidence | synchronization | cleanup | other`
- Ownership effect: `none | transfer-proposed | transfer-recorded`
- Replacement lease or transfer record: `not applicable` unless ownership effect is `transfer-recorded`

A GitHub login is not a sufficient worker-instance identity when several workers share the account. If the current owner identity is unknown, say so. Do not invent identity from the shared GitHub author account.

## Assistance claim

Record this as one top-level comment in the owning issue before substantive work when the helper will create a branch, mutable artifact, or focused execution surface.

```text
FIELDWORK ASSISTANCE CLAIM
Owning repository: <owner/repo>
Owning issue number: <number>
Assistance ID: <stable public-safe id>
State: claimed
Helper worker instance: <public-safe id>
Owner worker instance: <public-safe id or unknown>
Target artifact: <qualified repository, PR or branch, and exact head>
Assistance type: <type>
Question: <bounded question>
Expected output: <artifact or receipt>
Owned output: <separate branch, path, or issue-only note>
Input generation: <exact code and governing-record generations>
Ownership effect: none | transfer-proposed | transfer-recorded
Replacement lease or transfer record: <qualified exact record or not applicable>
Stop condition: <bounded stop>
Upstream contact authorized: no | exact authority
```

The resulting repository-qualified owning-issue comment is the authoritative claim receipt. A commit or workflow artifact may mirror the claim, but it cannot replace that comment. A completion without an exact authoritative owning-issue claim remains unresolved and non-composable.

`transfer-recorded` is valid only when `Replacement lease or transfer record` names a separate authoritative coordination record that already assigns the replacement writer. The assistance claim is never that assigning record. Without exact separate authority, use `none` or `transfer-proposed`.

## Assistance completion

Post the completed receipt in the owning issue and retain matching information in the helper output or pull-request description.

```text
FIELDWORK ASSISTANCE
Owning repository: <same owner/repo as claim>
Owning issue number: <same issue number as claim>
Assistance ID: <same id as claim>
State: complete
Authoritative claim receipt: <owner/repo#issue-number-comment-id>
Optional claim mirrors: <qualified commit/artifact locators or none>
Helper worker instance: <same public-safe id as claim>
Owner worker instance: <public-safe id or unknown>
Target input observed: <qualified exact observed generation>
Target generation at completion: <qualified exact current generation or unknown>
Input currentness at completion: exact | moved | unknown
Currentness observed at: <timestamp>
Currentness observation source: <qualified repository/API/receipt source>
Assistance type: <type>
Output: <qualified artifact, branch, PR, commit, test, review, or recipe>
Output generation: <qualified exact head, digest, or comment locator>
Finding or repair: <compact technical result>
Validation: <exact runs, commands, or source-read boundary>
Ownership effect: none | transfer-proposed | transfer-recorded
Replacement lease or transfer record: <qualified exact record or not applicable>
Owner action: none | inspect | reconcile | compose | acknowledge | record transfer
Supersedes: <none or qualified prior assistance completion/supersession>
Upstream contact authorized: no | exact authority
```

A moved or unknown input remains useful historical evidence, but the owner or coordinator must reconcile it against the current target before composition. The completion receipt must not describe moved or unknown assistance as current, accepted, or directly composable.

When `Ownership effect` is `transfer-recorded`, the completion must repeat the exact separate lease or transfer record. If that record is absent, inaccessible, stale, ambiguous, or does not assign the named replacement writer, effective ownership remains unchanged.

## Assistance supersession

Use an explicit supersession event rather than editing or deleting the old receipt.

```text
FIELDWORK ASSISTANCE SUPERSESSION
Owning repository: <same owner/repo as prior event>
Owning issue number: <same issue number as prior event>
Assistance ID: <same id as prior event>
State: superseded
Prior receipt: <qualified exact completion or supersession locator>
Authoritative claim receipt: <qualified owning-issue claim locator>
Helper worker instance: <public-safe id>
Owner worker instance: <public-safe id or unknown>
Target generation at supersession: <qualified exact generation or unknown>
Input currentness at supersession: exact | moved | unknown
Currentness observed at: <timestamp>
Currentness observation source: <qualified exact source>
Supersession reason: <bounded reason>
Evidence transferred: <qualified exact outputs/receipts or none>
Evidence rejected: <qualified exact outputs/receipts and reason or none>
Evidence retained: <qualified exact historical outputs/receipts or none>
Replacement output or Assistance ID: <qualified output or replacement composite key, or none>
Ownership effect: none | transfer-proposed | transfer-recorded
Replacement lease or transfer record: <qualified exact record or not applicable>
Owner action: none | inspect | reconcile | compose | acknowledge | record transfer
Upstream contact authorized: no | exact authority
```

A conflicting duplicate, missing prior locator, changed chain ID, or unlinked supersession remains unresolved rather than being silently selected.

## Legacy pre-ID reconciliation

Assistance claims and completions created before this identity contract remain historical evidence. Do not edit them in place, infer an Assistance ID, or silently index them as current events.

To adopt legacy evidence, create a new reconciliation event with a fresh composite event key:

```text
FIELDWORK ASSISTANCE LEGACY RECONCILIATION
Owning repository: <owner/repo>
Owning issue number: <number>
Assistance ID: <new stable id>
State: legacy-reconciled
Legacy claim receipt: <qualified exact locator or unknown>
Legacy completion receipt: <qualified exact locator or unknown>
Helper worker instance: <public-safe id or unknown>
Owner worker instance: <public-safe id or unknown>
Current target generation: <qualified exact generation or unknown>
Input currentness: exact | moved | unknown
Currentness observed at: <timestamp>
Currentness observation source: <qualified exact source>
Evidence adopted: <qualified exact evidence and limits>
Evidence not adopted: <qualified exact evidence and reason or none>
Ownership effect: none | transfer-proposed | transfer-recorded
Replacement lease or transfer record: <qualified exact record or not applicable>
Owner action: none | inspect | reconcile | compose | acknowledge | record transfer
Upstream contact authorized: no | exact authority
```

Legacy reconciliation never infers ownership transfer or independent-review eligibility from the old text. Conflicting attempted migrations remain unresolved.

## Discovery rule

A worker resuming an owned artifact should inspect the owning issue for assistance claims, completions, supersessions, and legacy reconciliations newer than the last assistance receipt or target generation they observed.

Correlate current claim/completion/supersession events by the composite key `(owning repository, owning issue number, Assistance ID)` and the exact authoritative claim receipt. Correlate legacy reconciliation by its fresh composite key and exact legacy locators. Do not correlate only by shared author, timestamp, issue number, target, or assistance type.

A coordinator or future router may index these blocks only after validating the observed grammar and fully qualified locators. It must reject duplicate composite keys with conflicting fields, unlinked events, inaccessible required records, and unknown currentness. It must not infer worker identity, ownership, review independence, or transfer from assistance activity.

When evidence changes another assignment's premise, post the completion or supersession receipt in both relevant coordination records, following `COORDINATION.md`, while retaining one authoritative owning-issue event chain.

## Ownership boundary

- `review`, `reproduction`, `regression`, `evidence`, and `repair-stack` normally have ownership effect `none`.
- A separate stacked branch belongs to the helper only; the target branch remains with its recorded writer.
- `transfer-proposed` requests a change but grants no mutation authority.
- `transfer-recorded` is valid only when the applicable coordination owner separately records the exact replacement lease or handoff and the receipt cites that fully qualified record.
- An assistance claim, completion, supersession, reconciliation, branch, review, or output is never itself a writer lease or transfer record.
- Silence, expiry, inactivity, a completed helper output, or a shared GitHub author never performs a transfer.
- Assistance receipts do not establish independent-review eligibility; review receipts must evaluate that separately.

## Reconciliation and retirement

When the owner composes the assistance output, record the consumed composite event key, authoritative claim receipt or exact legacy locators, output generation, reconciled target generation, and resulting canonical generation. Do not erase the helper receipt.

Mark an obsolete assistance output superseded only after its evidence is transferred or deliberately rejected with a reason through the explicit supersession block. Historical and legacy evidence remains available with its limits.
