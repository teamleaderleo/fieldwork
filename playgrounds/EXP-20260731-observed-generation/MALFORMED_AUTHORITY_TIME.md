# Malformed canonical authority timestamp repair

Canonical combined carrier: PR #385  
Exact base/source carrier: PR #376 at `7dec6db18de57d61bb903eeefeeb87774f0776b2`  
Historical component composition: PR #382 at `7be14cacb498d4a32d279b76e2e96237fb71c809`  
Parent projection-integrity source: PR #366 at `fa890d72589d36c6a0275c969183c9bf5bb3d37f`  
Original source blob: `reconcile.py@9e664220b3b024b92cbbc4444c15e87545cbd3cd`  
Work class: deterministic mechanism repair  
Upstream contact authorized: no

## Defect

`_authority_conditions()` parsed a canonical `expires_at` directly in the expiry condition. A malformed string, timezone-naive string, or non-string value raised before any projection was returned. One bad action therefore aborted reconciliation for every unrelated action, source condition, carrier condition, and continuity record.

PR #376 proved the bounded patch against the exact source blob with a disposable zero-fuzz patch workflow. That carrier passed:

- malformed authority repair `30633755335`, job `91166095752`;
- observed-generation parent matrix `30633755674`;
- playground/context integrity `30633755432`;
- Fieldwork integrity `30633756274`.

Those receipts remain historical exact-source evidence.

## Canonical composition

The canonical `reconcile.py` parses each non-null action expiry inside its own bounded guard.

On `AttributeError`, `TypeError`, or `ValueError` from the current parser boundary it:

- sets only that action's effective authority to `denied`;
- emits `AuthorityUsable = Unknown / InvalidAuthorityTime`;
- preserves the exact malformed input in the condition receipt;
- continues reconciling unrelated actions.

The explicit `AttributeError` fence remains necessary because `_parse_time()` calls `.replace()` before type validation. Valid expired, current, denied, absent, revocation-bounded, revoked, and unresolved paths are unchanged.

A malformed global observation boundary remains projection-wide invalid rather than being reclassified as an action-local fact.

## Native and transfer controls

The canonical `test_reconcile.py` matrix:

1. covers malformed text, timezone-naive text, and a non-string expiry;
2. requires only the malformed action to become `Unknown / InvalidAuthorityTime` and denied;
3. requires an unrelated bounded action to remain authorized;
4. requires a current revocation-bounded action to remain authorized;
5. composes the resulting projection through PR #366's derived-integrity/currentness helper;
6. proves canonical record and live facts remain byte-for-byte unchanged;
7. retains malformed global `observed_at` as a projection-wide invalid boundary.

The retained transfer module additionally:

- verifies the required native methods still exist;
- compares malformed text, timezone-naive text, and integer expiry directly against `condition["inputs"]["expires_at"]`, without normalization or stringification;
- requires all three to remain `Unknown / InvalidAuthorityTime`;
- runs `git apply --reverse --check` so the historical patch must still correspond exactly to the composed canonical source;
- imports the native test module rather than exporting its `TestCase` class into future discovery.

The dedicated patch-application workflow is removed. The exact patch remains historical provenance, not a second implementation carrier.

## Receipt history

Component canonical composition at PR #382 head `7be14cacb498d4a32d279b76e2e96237fb71c809` passed:

- observed-generation run `30637888075`, job `91180040904`: 17 reconciliation and 9 decision-currentness controls;
- playground/context integrity `30637888040`;
- Fieldwork integrity `30637888158`.

The transfer-control increment at PR #385 source head `44b438f16c3335b53dc0a3f39050803b27853f8a` passed:

- observed-generation run `30638936183`, job `91183623044`: 17 native, 3 transfer, and 9 decision-currentness controls;
- playground/context integrity `30638936228`;
- Fieldwork integrity `30638936124`.

Those runs are valid historical receipts for their exact generated merge generations. PR #385 now targets PR #376 directly so one complete review surface contains both the canonical source repair and transfer controls. The current combined head must obtain its own exact-base gates before promotion.

## Boundary

Malformed per-action canonical expiry is a fail-closed action fact. Schema admission that prevents malformed canonical records before reconciliation remains complementary.

This remains a standard-library mechanism experiment. It does not establish PR #306 compatibility, production mutation safety, lease assignment, merge/release/deployment authority, credentials, private data, spending, or public-upstream interaction.
