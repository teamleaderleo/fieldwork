# Identity and authority — cross-domain view

## In simple words

Several Fieldwork and Linux Fieldwork cases are easiest to connect by asking two questions:

1. **Which object did we prove was safe/authorized?**
2. **Which object did we later act on?**

Two recurring families appear, and they should remain distinct.

## Family A — the validated identity goes stale before use

```text
validate/select object X under context C
→ retain pathname/cache ID/marker
→ context or binding changes
→ later action resolves the token again
→ action may target X' under C'
```

Examples:

- filesystem server validates a pathname, then an ancestor can change before the later path-based syscall;
- account selection cache remembers an account while active credential identity changes;
- setup validates a contained cleanup destination, then a durable marker is interpreted after filesystem state changes.

Useful invariant: `validated-identity-must-match-used-identity`.

Bug species: `validated-identity-goes-stale-before-use`.

### Hunt it

Search for:

- validation functions returning strings used after `await`;
- caches keyed by profile/name but not the authority generation that made the value valid;
- durable cleanup markers or work queues that store an instruction for later destructive action;
- mutable allowed-root, credential, namespace, symlink, or generation state between check and use.

### Repair families

The abstract repair is to preserve or renew identity proof. Concrete mechanisms differ:

```text
filesystem → descriptor/capability or bounded revalidation

auth cache → revalidate under current credentials / non-secret generation

deferred cleanup → canonical contained identifier + full preflight + current resolution check
```

The shared invariant transfers. The implementation usually does not.

## Family B — normalization destroys identity before validation

```text
raw identity contains meaningful distinction
→ broad normalizer erases it
→ validation/matching sees only collapsed representation
```

Examples:

- path object construction removes `.` components before a cache-key uniqueness validator can inspect them;
- character-set stripping intended to remove archive `./` syntax also changes `.hidden` and `../path` names.

Useful invariant: `normalization-preserves-semantic-identity`.

Bug species: `normalization-erases-semantic-distinction`.

### Hunt it

Look for generic helpers whose contract is wider than the protocol's intended equivalence:

```text
strip / trim
path normalization
case folding
decoding
Unicode normalization
separator collapsing
canonical cache-key construction
```

Always keep near-neighbor negative controls: values that look similar to structural syntax but are real object data.

## Why these two families are not the same

```text
Family A:
identity was valid, then became stale before action

Family B:
identity was changed before the validation/matching decision
```

Family A is about **time/context and rebinding**.

Family B is about **representation and equivalence**.

Both can lead to “checked one object, used another,” but their discriminators and repairs differ.
