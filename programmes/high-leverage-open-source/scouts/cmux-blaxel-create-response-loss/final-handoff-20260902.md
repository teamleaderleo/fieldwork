# CMUX Blaxel create response-loss final handoff

Date: 2026-09-02  
Programme: high-leverage-open-source  
Fieldwork issue: #928  
Worker: `chatgpt:gpt-5.6-sol`  
Upstream contact authorized: `false`

## Question

Can one logical CMUX Blaxel VM create survive provider response loss and process restart without creating a second sandbox, losing ownership of the first sandbox, replaying an ambiguous billing debit, or refunding a debit and later adopting the same machine for free?

## Current upstream boundary

Re-fetched `manaflow-ai/cmux` immediately before final promotion.

Current upstream `main`:

`5a453950eac6e765e9d2eeb98fa45a68016f98b9`

This is one unrelated iOS commit after the VM source revision used for the candidate matrix. The final repair branch was rebuilt as a single commit directly on this upstream tip.

Upstream remained read-only. No upstream issue, pull request, comment, review, reaction, branch, or source mutation was created.

## Proven bug

Original canonical regression head:

`6c268876c5695621ca2b4a227cd9b1fb6da5c0fb`

Owned-fork proof PR: `teamleaderleo/cmux#14`  
Execution carrier: `teamleaderleo/cmux#15`  
Run: `33549149038`  
Job: `99993998566`

Target-executed RED:

`same-key retry created B while response-lost provider effect A remained live and unowned`

The original failure sequence is:

1. CMUX durably owns logical request K but does not yet durably own a provider identity.
2. Blaxel create commits sandbox A.
3. The success response containing A's identity is lost.
4. CMUX records a retryable provider-create failure with no provider id.
5. Same-key retry reaches provider create again and creates B.
6. CMUX owns B while A remains live outside the CMUX registry.

## Repair candidates and disposition

### Candidate A — failed-row identity handoff

Candidate A kept a durable Blaxel create identity and handed it from a retryable failed row to the same-key successor.

Disposition: rejected as complete repair.

Reason: a process crash can leave the original row in `provisioning` with no provider id. Same-key retry then returns `VmCreateInProgressError`; failed-row successor handoff never runs. Exact provider attempt identity must be resumable from the original row.

### Candidate B — resumable same-attempt provider protocol

Owned branch:

`fieldwork/blaxel-create-response-loss-resume-20260901`

Product commit:

`f11eda12dbf85edc1f961ebe5c9db9adba36e767`

Successful execution:

- run `33577608651`
- job `100084895691`

Candidate B established the provider-side protocol:

- durable `providerMetadata.createIdentity`;
- deterministic Blaxel sandbox name derived from that identity;
- identified creates use `POST /sandboxes?createIfNotExist=true`;
- ambiguous POST attempts read the exact deterministic sandbox before deciding what happened;
- stale `provisioning` row can be atomically claimed after the request timeout and replay the same provider identity;
- provider A committed while DB lacks `provider_vm_id` is adopted as A rather than followed by B;
- destroy after recovery deletes the recovered A;
- genuinely new logical request gets a new external attempt identity.

Disposition: provider-side repair proven GREEN, but insufficient as the final crash protocol because the durable identity existed before billing reservation. A crash before billing could later resume compute without a proven debit.

### Candidate C-plus — provider-start fence + indeterminate billing retention

Candidate C added a durable provider-start phase marker and then uncovered one more accounting edge during implementation.

The first edge was the billing→provider crash gap: Stack's server item decrement has no per-operation idempotency token in the inspected contract, so a stale row created before billing cannot safely replay billing after restart. Provider work must fail closed until CMUX has durable evidence that the billing call returned successfully.

The second edge was refund-on-ambiguity: the existing workflow refunded every provider-create error. For an ambiguous Blaxel create, that could mean A committed, response/readback stayed unknown, CMUX refunded the credit, then a later same-key retry adopted A. That would fix machine ownership but leave running compute after a refund.

The final repair therefore combines:

1. durable create identity before external create;
2. billing reservation;
3. durable `providerCreateReady=true` only after billing returned success;
4. provider create/replay of the exact identity only after the ready marker is durable;
5. explicit `provider_create_indeterminate` classification when an ambiguous POST cannot yet be reconciled by exact GET;
6. indeterminate create remains `provisioning`, keeps the same idempotency key and exact provider identity, and retains the billing reservation;
7. later stale retry replays/adopts the same provider identity without another billing reservation;
8. definite provider failure keeps the ordinary refund + retry path.

## Final protocol

```text
logical request K
      |
      v
insert provisioning row R
  createIdentity = I
  providerCreateReady absent
      |
      v
billing.reserveCreate()
      |
      v
persist providerCreateReady = true
      |
      v
Blaxel POST deterministic sandbox(I)
      |
      +-- success ------------------------------> finalize R with provider id
      |
      +-- ambiguous response
             |
             v
        GET exact sandbox(I)
             |
             +-- found + matching -------------> adopt/finalize same R
             |
             +-- still unknown ----------------> keep R provisioning + billing held
                                                     |
                                                     v
                                          stale same-key retry claims R
                                                     |
                                                     v
                                          replay exact sandbox(I)
```

The provider-start fence is the authority boundary. A stale row without `providerCreateReady=true` cannot start compute and cannot replay the Stack debit.

## Lifecycle mapping

### Definite pre-effect provider failure

Expected/observed: compensate billing, mark retryable failure, same-key retry may make one provider VM. Canonical negative control remains GREEN.

### Response loss after provider commit

Expected/observed: deterministic exact identity is retained; exact GET or later replay adopts A. Provider state stays singleton.

### Crash before provider call

Two cases:

- before durable provider-ready fence: fail closed; zero provider calls and zero billing replay on stale retry;
- after durable provider-ready fence: stale retry replays the exact provider identity without a second billing reservation.

### Crash after provider success before provider-id commit

Expected/observed: stale retry uses the same durable ready identity and adopts/finalizes the same A.

### Crash after provider-id commit before visible success

Expected/observed: ordinary same-key replay returns the already-running row; no second provider create.

### Provider timeout / unknown external fate

Expected/observed in the provider-native discriminator: mark the create outcome indeterminate, retain billing and exact identity, and block blind new identity. Later exact replay can adopt A.

### Restart

Expected/observed: only ready + identified stale rows are claimable for provider replay. Pre-fence stale rows remain fail-closed.

### Same logical idempotency key

Expected/observed: converges on one external create identity and one provider machine.

### Genuinely new request

Expected/observed: receives a different create identity and may create a different VM.

### Destroy after ambiguous recovery

Expected/observed: recovered provider state is removed by normal destroy ownership path.

## Candidate C-plus executed receipts

Owned test/product branch:

`fieldwork/blaxel-create-response-loss-billing-fence-20260901`

Executed product head:

`49ed8e224a91bb8d05a817b23377fd59e7ff1224`

Carrier branch:

`fieldwork/blaxel-create-response-loss-billing-fence-carrier-20260901`

Successful run:

- run `33580038711`
- job `100092189411`

This run proved both new discriminators RED on Candidate B before applying the repair:

- stale Blaxel row before durable billing fence incorrectly reached provider;
- indeterminate provider create incorrectly refunded billing / left the exact-attempt protocol unsafe.

After materializing Candidate C-plus, the same carrier proved GREEN:

- billing/provider phase fence;
- indeterminate reservation retention and exact-attempt adoption;
- restart-before-provider recovery;
- provider-committed / DB-missing-provider-id recovery;
- same-key convergence;
- genuinely new request gets a new identity;
- destroy after recovery;
- provider-native response-loss repair;
- Blaxel provider controls;
- existing transient provider-create retry control;
- canonical definite pre-effect provider failure.

The original canonical ambiguous gateway fake intentionally remains RED on repaired source because it fabricates a fresh provider id on every gateway create and ignores the provider-attempt identity contract. It remains the original bug proof/negative oracle; provider-native tests exercise the repaired contract.

## Clean final branch and validation

Final base branch in owned fork:

`fieldwork/blaxel-create-response-loss-final-base-20260902`

Base SHA:

`5a453950eac6e765e9d2eeb98fa45a68016f98b9`

Final repair branch:

`fieldwork/blaxel-create-response-loss-final-20260902`

Single repair commit:

`c3ecae669d87c31d0126c320177bd3a5dc6e1309`

The final commit has exactly seven changed files:

- `web/services/vms/drivers/blaxel.ts`
- `web/services/vms/providerErrors.ts`
- `web/services/vms/repository.ts`
- `web/services/vms/workflows.ts`
- `web/tests/vm-blaxel-create-billing-fence.test.ts`
- `web/tests/vm-blaxel-create-response-loss-repair.test.ts`
- `web/tests/vm-blaxel-create-response-loss-resume.test.ts`

Final validation carrier:

`fieldwork/blaxel-create-response-loss-final-carrier-20260902`

Validation run:

- run `33580271082`
- job `100092895157`
- conclusion: success

The validation checked:

- final HEAD is exactly `c3ecae669...`;
- its only parent is current upstream `5a453950...`;
- bounded diff is exactly the seven files above;
- those seven files are byte-for-byte the executed Candidate C-plus blobs;
- billing-fence/indeterminate tests GREEN;
- restart/adoption tests GREEN;
- provider-native response-loss repair GREEN;
- Blaxel provider controls GREEN;
- existing transient retry control GREEN;
- canonical definite pre-effect control GREEN;
- canonical ambiguous gateway fake remains the expected RED oracle limitation.

## Owned-fork repair PR

PR: `teamleaderleo/cmux#49`  
URL: https://github.com/teamleaderleo/cmux/pull/49  
Title: `Fix Blaxel create response-loss reconciliation`

The PR body begins with `## In simple words` and records the protocol, lifecycle behavior, receipts, and residual uncertainty.

## Negative results / failed attempts worth retaining

1. Failed-row identity handoff alone is insufficient because restart can leave the original row `provisioning`.
2. Candidate B's same-attempt provider resume alone is insufficient because it permits pre-billing stale rows to reach provider.
3. The first Candidate C carrier run (`33578507039`, job `100087596614`) failed during patch materialization with `fresh provider metadata source: expected one match, found 2`. That was a carrier string-match defect after the target RED had already executed; it was not a product-test failure.
4. The initial Candidate B runs exposed two test-harness defects: missing team ownership on destroy and a fake that incorrectly required new logical requests to reuse A's identity. Both were corrected before the successful Candidate B receipt.
5. The original gateway-level ambiguous fake is deliberately incompatible with the repaired provider identity contract and therefore remains RED on repaired source.

## Remaining uncertainty / residuals

1. **Billing ambiguity before provider-ready commit.** Stack's inspected ordinary server-item mutation exposes `tryDecreaseQuantity(amount)` without a per-operation idempotency token. If the billing call committed but CMUX cannot durably record `providerCreateReady`, the repair fails closed and may leave charged credit with no compute. That is safer for provider ownership than replaying billing or starting compute, but it is an accounting reconciliation case.
2. **Refund failure after a definite provider-create failure.** The existing compensation path can still encounter an external refund failure. A subsequent retry may then reserve again. This is an existing billing-compensation concern and was kept outside the bounded Blaxel response-loss ownership repair.
3. **Stale claim threshold.** Recovery currently waits 11 minutes, one minute beyond the 10-minute API create timeout. Review should keep that threshold aligned with the longest legitimate active create so a live request is not reclaimed prematurely.
4. **Blaxel live fault injection.** `createIfNotExist=true`, deterministic identity, and exact read-after-ambiguity are exercised through provider-native tests and the API contract used by the adapter. No live production response-cut fault injection was performed.
5. **Other providers.** This protocol is Blaxel-specific. Other provider create/idempotency contracts remain separate work.

## Upstream overlap

The only upstream movement during finalization was `5a453950eac6e765e9d2eeb98fa45a68016f98b9`, an unrelated iOS change whose parent is the VM source snapshot used by the candidate tests. The final branch was rebuilt on that commit and revalidated. No upstream VM overlap was observed during this lane.

## Final finding

The original orphan bug is a durable identity / ambiguous external-effect problem, not a generic retry problem. The repair is strongest when provider identity and phase authority are explicit:

- identity exists before external create;
- billing must cross a durable provider-start fence before compute;
- ambiguous provider fate keeps the exact attempt and billing reservation alive;
- retry reconciles/replays the exact attempt rather than creating another identity;
- only definite failure is compensated and treated as a fresh retry opportunity.

That protocol is now implemented on the owned fork, target-executed GREEN, reconstructed as one clean commit on current upstream, and opened as owned-fork PR #49.

Upstream `manaflow-ai/cmux` remained read-only for the entire investigation and implementation lane.