# Malformed canonical authority timestamp repair

Parent repair carrier: PR #376 exact head `7dec6db18de57d61bb903eeefeeb87774f0776b2`  
Parent projection-integrity source: PR #366 exact head `fa890d72589d36c6a0275c969183c9bf5bb3d37f`  
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

Those receipts remain historical evidence for the exact carrier generation.

## Canonical composition

The canonical `reconcile.py` now parses each non-null action expiry inside its own bounded guard.

On `AttributeError`, `TypeError`, or `ValueError` from the current parser boundary it:

- sets only that action's effective authority to `denied`;
- emits `AuthorityUsable = Unknown / InvalidAuthorityTime`;
- preserves the exact malformed input in the condition receipt;
- continues reconciling unrelated actions.

The explicit `AttributeError` fence remains necessary because `_parse_time()` calls `.replace()` before type validation. Valid expired, current, denied, absent, revocation-bounded, revoked, and unresolved paths are unchanged.

## Native controls

The canonical `test_reconcile.py` matrix now:

1. covers malformed text, timezone-naive text, and a non-string expiry;
2. requires only the malformed action to become `Unknown / InvalidAuthorityTime` and denied;
3. requires an unrelated bounded action to remain authorized;
4. requires a current revocation-bounded action to remain authorized;
5. composes the resulting projection through PR #366's derived-integrity/currentness helper;
6. proves canonical record and live facts remain byte-for-byte unchanged;
7. retains malformed global `observed_at` as a projection-wide invalid boundary.

The dedicated patch-application workflow is removed after receipt transfer. A safety boundary prevented deletion of the exact patch artifact, so the patch remains as historical evidence rather than being misclassified as a failed cleanup. The former patch harness is reduced to a transfer assertion that points to the native controls and no longer preserves the obsolete baseline-crash expectation.

## Boundary

Malformed per-action canonical expiry is a fail-closed action fact. A malformed global observation boundary remains projection-wide invalid. Schema admission that prevents malformed canonical records before reconciliation remains a complementary control.

This is still a standard-library mechanism experiment. It does not establish PR #306 compatibility, production mutation safety, lease assignment, merge/release/deployment authority, credentials, private data, spending, or public upstream interaction.
