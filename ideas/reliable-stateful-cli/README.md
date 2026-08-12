# Reliable stateful CLI — BDFL notebook

## In simple words

If we were the benevolent dictator for a stateful developer CLI, the product would treat **uncertainty, ownership, recovery, and machine-readable truth as first-class state**.

This notebook grew out of a tiny false-success bug in a package-manager tool command, but the useful ideas are broader. They apply to package managers, local runner stewards, deployment tools, project coordinators, database CLIs, and any program that manages durable external state.

This is exploratory Fieldwork material. It is not an upstream proposal and does not supersede project-specific contracts.

## The BDFL rules

### 1. Unknown is a value, not an empty collection

Never convert “could not establish state” into a normal empty result.

Aggregate operations should preserve both their observations and whether coverage was complete:

```json
{
  "complete": false,
  "observed": 3,
  "findings": ["receipt_unreadable"],
  "gaps": ["tool:black"]
}
```

A human summary may be concise. The underlying result must retain the epistemic difference between:

- zero things exist;
- zero matching things were observed;
- observation was incomplete;
- observation failed before a conclusion was possible.

### 2. Observe first; interpret second

The low-level state reader should preserve what it saw instead of forcing every irregularity into either a valid object or a fatal error.

A useful inventory can contain entries such as:

```text
healthy item
unexpected child
invalid identity
missing metadata
malformed metadata
missing runtime
unreadable path
foreign object
unknown ownership
```

Commands then decide which observations are fatal for their purpose.

### 3. Managed roots need positive ownership

A path configured through an environment variable or config file is not automatically safe to mutate.

A manager-owned root should identify itself with a versioned marker containing enough immutable identity to distinguish:

```text
unexpected object inside our root
```

from:

```text
we were pointed at an unrelated directory
```

The same filesystem observation may therefore produce a reversible quarantine action in a positively claimed root and **no destructive action** in an unclaimed root.

### 4. Hints are recovery interfaces

A `hint:` line is part of the product's recovery path. It should satisfy the same standard as a command:

- valid for the exact failure family;
- executable from the state that produced the failure;
- precise about the object the user will touch;
- reversible first when origin is uncertain;
- silent when the program lacks enough evidence to prescribe a universal repair.

“Run command X” is a bad hint when command X reads the same corrupted state and immediately fails.

### 5. Recovery actions carry confidence and safety separately

A suggested action has at least two independent properties:

```text
confidence: how sure are we that this action addresses the observed problem?
safety: what happens if the action was the wrong choice?
```

Examples:

```text
exact + read-only
exact + reversible
conditional + reversible
exact + destructive
conditional + destructive
```

Automation policy should consume both axes. Logical certainty does not make deletion automatically safe.

### 6. Desired intent should survive mutable runtime state

If the manager can rebuild an installation, worker, environment, deployment, or local service, retain the desired specification independently from the disposable runtime.

A broken environment should not erase the only copy of:

- what was requested;
- which version/source was selected;
- relevant options;
- public entrypoints/resources;
- enough provenance to reconstruct or explain it.

This turns repair from archaeology into reconciliation.

### 7. Build complete replacements before activation

For replaceable state, prefer generations:

```text
prepare generation N+1
validate generation N+1
publish generation N+1
switch one active pointer
verify freshly
retain N for a bounded rollback window
```

A process crash before the switch leaves N authoritative. Cleanup after the switch can fail independently without reviving N.

Activation and garbage collection are different transactions.

### 8. Public launchers/resources need their own ownership identity

A receipt saying “we once installed `black`” is weak evidence that a current public `black` executable still belongs to us.

Public resources should carry or admit recoverable provenance. Before overwriting or deleting a path, establish that the current object is still the object we own.

Foreign replacement wins the safety contest: preserve it and report the collision.

### 9. Retired resources should fail closed before cleanup

Suppose a new generation stops providing an entrypoint that an old generation exposed. Activation may happen before stale-launcher cleanup.

During that interval, the old launcher should resolve against the **current logical generation**, discover that the entrypoint is retired, and fail closed. It must never silently execute the previous generation.

### 10. Human output and machine output are different contracts

Human diagnostics should be allowed to improve. Automation should consume a versioned typed result.

A good machine contract has stable concepts such as:

```text
code
state/verdict
complete
findings
coverage gaps
object identity
recovery candidates
authority/authorizesMutation
receipt or observation identity
```

Avoid making scripts parse sentences that are written for people.

### 11. Successful process execution is evidence, not reconciliation

A command returning zero proves that one process reported success. It does not prove that the desired external state exists.

Mutation flows should end with a fresh observation and classify the result against the intended state.

### 12. Repair should be a normal product feature

Healthy use stays terse. Damaged state gets explicit tools:

```text
doctor/status
repair --dry-run
repair
history
rollback
quarantine
reconcile
```

These should be ordinary supported workflows, not secret emergency incantations.

## A generic state model

```text
DesiredSpec
   │
   ├── identity / provenance
   ├── policy
   └── intended resources

Observation
   │
   ├── complete? yes/no
   ├── typed findings
   └── gaps / unknowns

ReconciliationPlan
   │
   ├── exact preconditions
   ├── action confidence
   ├── action safety
   ├── rollback/compensation class
   └── authorisation requirement

ExecutionReceipt
   │
   └── attempt evidence

FreshObservation
   │
   └── proves or disproves reconciliation
```

This separation is more valuable than any particular command spelling.

## Origin experiment

The uv diagnostic work that triggered this notebook remains in `experiments/uv-21058-diagnostics/`. That experiment includes concrete error/hint prototypes, a generation/launcher model, and a filesystem state-machine toy. The broader rules above are intentionally extracted from that one repository and one bug.

## Status

**Preference-level design notes with some model-executed supporting evidence.** Project-specific adoption requires fresh source reading and should keep the smallest useful subset.
