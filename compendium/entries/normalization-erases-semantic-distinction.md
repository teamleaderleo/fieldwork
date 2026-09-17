# Normalization erases a semantic distinction

## Metadata

```json
{
  "schema": 1,
  "id": "normalization-erases-semantic-distinction",
  "kind": "bug-species",
  "maturity": "supported",
  "facets": {
    "domains": ["filesystems", "parsing", "caching"],
    "concerns": ["identity", "compatibility", "state-consistency"],
    "mechanisms": ["normalization", "canonicalization", "cache-key"],
    "triggers": ["representation-conversion", "edge-case-input"]
  },
  "aliases": ["over-normalization", "normalizer-erases-token-before-validation"],
  "relations": [
    {"type": "violates", "target": "normalization-preserves-semantic-identity"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#225",
    "teamleaderleo/linux-fieldwork#28"
  ]
}
```

## In simple words

A convenience normalizer performs a broader transformation than the contract allows, so two meaningfully different inputs become the same—or one input becomes a different object—before validation or matching can notice.

Examples from retained work include:

```text
PurePosixPath removes dot components
→ validator can no longer reject the original token
→ distinct request spellings alias one cache key
```

and:

```text
lstrip("./")
→ removes any run of '.' and '/'
→ archive member .hidden or ../path changes identity
```

## Typical signatures

- validation runs only after canonicalization;
- a generic `strip`, `trim`, `normalize`, or path constructor destroys evidence about the original spelling;
- cache keys alias inputs whose distinction matters to policy;
- a matcher sees a different object name from the archive/protocol consumer;
- negative controls with dotfiles, repeated separators, `..`, case, encoding, or Unicode expose the difference.

## Hunting questions

- Which input spellings are *actually* equivalent by contract?
- Which helper is being used, and what transformations does it perform beyond that contract?
- Does later validation need the pre-normalized components?
- Can the normalized form be safely used as an identity/cache key?
- Does the consumer reopen or report the original spelling later?

## Repair shape

Perform the narrow structural transformation explicitly. Validate security/identity-significant tokens before a lossy normalizer erases them. Retain original representations when later matching or reference rewriting needs them.

## Regression shape

Test both equivalent and near-neighbor non-equivalent inputs. A strong fixture proves that intended aliases still converge while dotfiles, traversal components, literal prefixes, or other meaningful tokens remain distinct.

## Limits and counterexamples

Normalization itself is not suspicious. The species requires a mismatch between the transformation and the governing identity contract. Aggressive canonicalization can be exactly correct when the protocol explicitly defines those inputs as equivalent.
