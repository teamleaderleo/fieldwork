# Fieldwork Assistance Receipt

## In simple words

Use this receipt when one worker helps work owned by another worker, especially when both appear under the same GitHub account. It records who helped, which exact generation they observed, what they produced, and whether ownership changed. Assistance never transfers a writer lease by implication.

## Identity and ownership

- Assistance ID:
- Assistance state: `claimed | complete | superseded`
- Claim receipt: exact comment, commit, or artifact identity; `not applicable` only while state is `claimed`
- Helper worker instance:
- Owner worker instance: `unknown` when the earlier record did not preserve one
- Owning coordination record:
- Claimed target artifact identity:
- Claimed input generation:
- Target generation at completion: `not applicable` while state is `claimed`
- Input currentness at completion: `exact | moved | unknown | not applicable`
- Assistance type: `review | reproduction | regression | repair-stack | evidence | synchronization | cleanup | other`
- Ownership effect: `none | transfer-proposed | transfer-recorded`
- Replacement lease or transfer record: `not applicable` unless ownership effect is `transfer-recorded`

A GitHub login is not a sufficient worker-instance identity when several workers share the account. Each claimed unit must use one stable assistance ID and one durable, non-secret worker-instance identifier. Use bounded opaque public-safe coordination values, for example:

```text
assist:<UTC date>:<short random or assignment id>
worker:<role>:<UTC date>:<short random or assignment id>
```

Both identifiers must be 1–160 ASCII characters, begin with the appropriate `assist:` or `worker:` prefix, and otherwise contain only lowercase letters, digits, `.`, `_`, `:`, or `-`. Whitespace, control characters, Unicode confusables, path separators, query fragments, and line breaks are invalid.

These identifiers must not contain credentials, tokens, private chat or session identifiers, personal data, hostnames, filesystem paths, provider request IDs, or other private infrastructure details. They are attribution and correlation metadata, not authentication, write authority, or proof of independent-review eligibility.

The same assistance ID appears in the claim, completion, and any supersession receipt. Never recycle an assistance ID for another bounded question or target generation.

## Assistance claim

Record this in the owning issue before substantive work when the helper will create a branch, mutable artifact, or focused execution surface.

```text
FIELDWORK ASSISTANCE CLAIM
Assistance ID: <stable public-safe id>
State: claimed
Helper worker instance: <public-safe id>
Owner worker instance: <public-safe id or unknown>
Owning coordination record: <issue>
Target artifact: <repository, PR or branch, and exact head>
Assistance type: <type>
Question: <bounded question>
Expected output: <artifact or receipt>
Owned output: <separate branch, path, or issue-only note>
Input generation: <exact code and governing-record generations>
Ownership effect: none | transfer-proposed | transfer-recorded
Replacement lease or transfer record: <exact record or not applicable>
Stop condition: <bounded stop>
Upstream contact authorized: no | exact authority
```

If the current owner identity is unknown, say so. Do not invent identity from the shared GitHub author account.

`transfer-recorded` is valid only when `Replacement lease or transfer record` names a separate authoritative coordination record that already assigns the replacement writer. The assistance claim is never that assigning record. Without exact separate authority, use `none` or `transfer-proposed`.

## Immutable claim fields and permitted transitions

The completion receipt must repeat these claim fields exactly:

- Assistance ID;
- Helper worker instance;
- Owning coordination record;
- Assistance type;
- Target artifact;
- Input generation.

Target movement never rewrites the claimed target artifact or input generation. Record movement only through `Target generation at completion` and `Input currentness at completion`.

The completion must repeat the claimed owner worker value, including `unknown`, unless `Ownership effect` is `transfer-recorded` and the cited separate lease or transfer record assigns the replacement writer named by the completion.

The completion must repeat the claim's ownership effect except that `none` or `transfer-proposed` may advance to `transfer-recorded` when the exact separate assigning record already exists. `transfer-recorded` must repeat the same assigning record. No other ownership-effect transition is valid under the same Assistance ID.

When the bounded question, helper, coordination record, assistance type, target identity, input generation, owner identity without exact transfer authority, or ownership transition changes outside these rules, supersede the claim and create a new Assistance ID. A mismatched completion remains unresolved and must not be treated as complete, current, accepted, composable, or ownership-changing.

## Assistance completion

Post the completed receipt in the owning coordination record and retain the same information in the helper output or pull-request description.

```text
FIELDWORK ASSISTANCE
Assistance ID: <same id as claim>
State: complete
Claim receipt: <exact claim comment, commit, or artifact>
Helper worker instance: <repeat claim exactly>
Owner worker instance: <repeat claim exactly, or exact replacement writer assigned by the cited record>
Owning coordination record: <repeat claim exactly>
Claimed target artifact: <repeat Target artifact exactly>
Claimed input generation: <repeat Input generation exactly>
Target generation at completion: <exact current generation or unknown>
Input currentness at completion: exact | moved | unknown
Assistance type: <repeat claim exactly>
Output: <exact artifact, branch, PR, commit, test, review, or recipe>
Output generation: <exact head, digest, or comment id>
Finding or repair: <compact technical result>
Validation: <exact runs, commands, or source-read boundary>
Ownership effect: <repeat claim, or advance none/transfer-proposed to transfer-recorded with exact authority>
Replacement lease or transfer record: <repeat exact assigning record or not applicable>
Owner action: none | inspect | reconcile | compose | acknowledge | record transfer
Supersedes: <none or exact assistance receipt>
Upstream contact authorized: no | exact authority
```

A moved or unknown input remains useful historical evidence, but the owner or coordinator must reconcile it against the current target before composition. The completion receipt must not describe moved or unknown assistance as current, accepted, or directly composable.

When `Ownership effect` is `transfer-recorded`, the completion must repeat the exact separate lease or transfer record. If that record is absent, inaccessible, stale, does not assign the named replacement writer, or differs from a `transfer-recorded` claim, effective ownership remains unchanged and the completion is unresolved.

## Discovery rule

A worker resuming an owned artifact should inspect the owning issue for assistance claims and completions newer than the last assistance receipt or target generation they observed. Correlate events by Assistance ID and exact Claim receipt, not only by shared author, timestamp, issue, target, or assistance type.

The coordinator or a future router may index these blocks, but it must reject duplicate Assistance IDs with conflicting fields, reject completions that violate the immutable-field or transition rules, and must not infer a transfer from assistance activity.

When evidence changes another assignment's premise, post the completion receipt in both relevant coordination records, following `COORDINATION.md`.

## Ownership boundary

- `review`, `reproduction`, `regression`, `evidence`, and `repair-stack` normally have ownership effect `none`.
- A separate stacked branch belongs to the helper only; the target branch remains with its recorded writer.
- `transfer-proposed` requests a change but grants no mutation authority.
- `transfer-recorded` is valid only when the applicable coordination owner separately records the exact replacement lease or handoff and the receipt cites that record.
- An assistance claim, completion, branch, review, or output is never itself a writer lease or transfer record.
- Silence, expiry, inactivity, a completed helper output, or a shared GitHub author never performs a transfer.
- Assistance receipts do not establish independent-review eligibility; review receipts must evaluate that separately.

## Reconciliation and retirement

When the owner composes the assistance output, record the consumed Assistance ID, claim receipt, output generation, reconciled target generation, and resulting canonical generation. Do not erase the helper receipt.

Mark an obsolete assistance output `superseded` only after its evidence is transferred or deliberately rejected with a reason. The supersession record must repeat the Assistance ID and cite the exact completion or earlier supersession receipt it replaces. A conflicting duplicate, invalid field transition, or unlinked completion remains unresolved rather than being silently selected.
