# First applications of the reliable-stateful-CLI notebook

## In simple words

The first useful test of these notes was whether they produced **different local changes** in different repositories.

They did.

The notebook is a source of questions, not a universal framework to import wholesale.

## SmolRunner — separate diagnosis confidence from repair safety and authority

SmolRunner already had most of the reliable-control-loop policy before this notebook existed:

- exact ownership before mutation;
- durable checkpoints;
- fresh post-action observation;
- rollback/compensation classes;
- repair budgets;
- circuit breakers;
- host-local vetoes;
- explicit autonomy levels;
- a public operator error catalogue with retry/remediation classes.

So adding another generic `doctor` or hint framework would have duplicated concepts the project already owned.

The missing seam was narrower: one public error can say `remediation: repair`, but a future automatic controller still needs to know whether one **concrete proposed repair** is supported by exact evidence, how safe it is, and whether it is merely advisory, plan-only, or eligible for later policy evaluation.

Owned experiment: `teamleaderleo/smolrunner#433`.

That slice introduces three separate axes:

```text
confidence
  exact | conditional | insufficient

safety
  read_only | reversible | compensating | irreversible

applicability
  advisory_only | plan_only | policy_eligible
```

`policy_eligible` explicitly remains non-authorizing. Mutating candidates still require the repository's existing ownership, budget, checkpoint, verification, rollback/compensation, and circuit-breaker machinery.

### General lesson

**A diagnostic answer and a mutation permission are different objects.**

The useful abstraction boundary was between an already-good public error catalogue and an already-good authority/execution model.

## Stensibly — separate outcome verdict from observation coverage

Stensibly already had bounded GitHub outcome tools such as repository health and CI diagnosis.

A small epistemic ambiguity remained in `github_ci_diagnose`: the command could correctly conclude that CI was failing while optional failed-job step retrieval failed. The nested failed-job object said `detailState: unavailable`, but the top-level result still gave callers no compact answer to:

```text
Did this operation obtain every evidence class I asked for?
```

Owned change: `teamleaderleo/stensibly#1472`.

The additive result contract introduces:

```json
{
  "coverage": {
    "version": 1,
    "state": "complete | partial | blocked",
    "requested": ["..."],
    "gaps": ["..."]
  }
}
```

That lets these two facts coexist cleanly:

```text
verdict: failing
coverage: partial
```

The failing verdict remains justified by observed workflow/job evidence. Coverage tells the caller that requested step-level detail was unavailable.

If the caller requests summary-only diagnosis, the same failed CI can be:

```text
verdict: failing
coverage: complete
```

because step details were never part of the requested evidence set.

Repository health uses the same small vocabulary to distinguish complete observation from an attachment-blocked read.

### General lesson

**Completeness is relative to the requested observation contract.**

Do not mark a result partial merely because richer information exists somewhere. Mark it partial when promised/requested evidence was unavailable.

## Why these applications are intentionally different

The original package-manager investigation could tempt us to invent one grand `Finding + Hint + Repair + Coverage + Authority` framework and push it into every repository.

That would be backwards.

The reusable questions are:

1. What did we observe?
2. Was the requested observation complete?
3. How confident are we in the diagnosis?
4. What response follows from that exact evidence?
5. How safe or reversible is it?
6. Who owns the affected object?
7. What grants mutation authority?
8. What fresh observation proves success?

Each project should answer only the missing questions at its native abstraction boundary.

SmolRunner already answered 1, 2, 6, 7, and 8 deeply; its useful addition was richer typing around 3–5.

Stensibly already had good bounded outcomes and durable mutation authority; its useful addition was making question 2 explicit on read outcomes.

The package-manager toy still benefits most from explicit ownership, generations, public-resource provenance, and rollback.

That divergence is evidence that the notebook is functioning as design guidance instead of becoming a cargo-cult library.
