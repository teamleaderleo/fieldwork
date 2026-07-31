# Fieldwork Assistance Receipt

## In simple words

Use this receipt when one worker helps work owned by another worker, especially when both appear under the same GitHub account. It records who helped, which exact generation they observed, what they produced, and whether ownership changed. Assistance never transfers a writer lease by implication.

## Identity and ownership

- Assistance state: `claimed | complete | superseded`
- Helper worker instance:
- Owner worker instance: `unknown` when the earlier record did not preserve one
- Owning coordination record:
- Target artifact or branch:
- Exact observed input generation:
- Assistance type: `review | reproduction | regression | repair-stack | evidence | synchronization | cleanup | other`
- Ownership effect: `none | transfer-proposed | transfer-recorded`
- Replacement lease record: `not applicable` unless ownership effect is `transfer-recorded`

A GitHub login is not a sufficient worker-instance identity when several workers share the account. Each claimed unit should use one durable, non-secret identifier, for example:

```text
worker:<role-or-system>:<UTC timestamp>:<short nonce or assignment id>
```

The identifier is coordination metadata, not proof of independent-review eligibility.

## Assistance claim

Record this in the owning issue before substantive work when the helper will create a branch, mutable artifact, or focused execution surface.

```text
FIELDWORK ASSISTANCE CLAIM
State: claimed
Helper worker instance: <id>
Owner worker instance: <id or unknown>
Owning coordination record: <issue>
Target artifact: <repository, PR or branch, and exact head>
Assistance type: <type>
Question: <bounded question>
Expected output: <artifact or receipt>
Owned output: <separate branch, path, or issue-only note>
Input generation: <exact code and governing-record generations>
Ownership effect: none | transfer-proposed | transfer-recorded
Stop condition: <bounded stop>
Upstream contact authorized: no | exact authority
```

If the current owner identity is unknown, say so. Do not invent identity from the shared GitHub author account.

## Assistance completion

Post the completed receipt in the owning coordination record and retain the same information in the helper output or pull-request description.

```text
FIELDWORK ASSISTANCE
State: complete
Helper worker instance: <id>
Owner worker instance: <id or unknown>
Owning coordination record: <issue>
Target input: <exact observed generation>
Assistance type: <type>
Output: <exact artifact, branch, PR, commit, test, review, or recipe>
Output generation: <exact head, digest, or comment id>
Finding or repair: <compact technical result>
Validation: <exact runs, commands, or source-read boundary>
Ownership effect: none | transfer-proposed | transfer-recorded
Owner action: none | inspect | compose | acknowledge | record transfer
Supersedes: <none or exact receipt>
Upstream contact authorized: no | exact authority
```

## Discovery rule

A worker resuming an owned artifact should inspect the owning issue for assistance claims and completions newer than the last generation they observed. The coordinator or a future router may index these blocks, but it must not infer a transfer from assistance activity.

When evidence changes another assignment's premise, post the completion receipt in both relevant coordination records, following `COORDINATION.md`.

## Ownership boundary

- `review`, `reproduction`, `regression`, `evidence`, and `repair-stack` normally have ownership effect `none`.
- A separate stacked branch belongs to the helper only; the target branch remains with its recorded writer.
- `transfer-proposed` requests a change but grants no mutation authority.
- `transfer-recorded` is valid only when the applicable coordination owner separately records the replacement lease or handoff.
- Silence, expiry, inactivity, a completed helper output, or a shared GitHub author never performs a transfer.
- Assistance receipts do not establish independent-review eligibility; review receipts must evaluate that separately.

## Reconciliation and retirement

When the owner composes the assistance output, record the consumed output generation and the resulting canonical generation. Do not erase the helper receipt. Mark obsolete assistance outputs `superseded` only after their evidence is transferred or deliberately rejected with a reason.
