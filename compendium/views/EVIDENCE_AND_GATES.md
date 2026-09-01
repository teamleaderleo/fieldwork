# Evidence and CI gates

## In simple words

CI color is a property of a particular execution path. It is not automatically the evidence class needed for the claim.

Two complementary mistakes recur:

```text
green aggregate
+ required discriminator never ran
= insufficient evidence
```

and:

```text
red aggregate
+ failure occurred before candidate/relevant test ran
= not automatically candidate failure
```

## Green without the proof

Use `required-discriminator-must-not-skip-green` when a behavior claim depends on one platform, capability, helper, device, privilege, or integration test.

Check:

- helper built?
- capability actually established?
- test executed rather than skipped/ignored?
- behavioral assertion reached?
- result tied to exact candidate head?

A green suite summary is compatible with **unknown** evidence if the required discriminator never executed.

Bug species: `suite-green-while-discriminator-skipped`.

## Red before the proof boundary

Use `classify-red-gate-at-first-failing-boundary` for broad CI failures.

Walk the execution path:

```text
checkout
→ setup/dependencies
→ generated sources
→ broad build
→ changed target compile
→ relevant test starts
→ behavioral assertion
```

Name the first failing owner and ask whether changed code or the claimed behavior was reached.

A red badge can mean:

- candidate compile/test failure;
- unrelated broad target failure;
- missing generated fixture;
- capability/environment failure;
- workflow/tooling defect;
- packaging/integration failure before candidate execution.

Classification is evidence; badge color alone is not.

## The shared principle

```text
claim
→ required discriminator
→ prerequisite chain
→ exact executed boundary
→ narrowest truthful evidence class
```

Do not upgrade:

```text
prepared test → executed test
focused pass → full gate
suite green → proof of skipped behavior
broad red → candidate regression
```

without the missing evidence.

## Why this belongs in the bug compendium

Evidence bugs alter engineering decisions even when product code is correct. They can promote false positives, bury real candidates under unrelated red infrastructure, or let a skipped proof silently become a green receipt.

The bestiary therefore includes bugs in the **grammar of proof**, not only bugs in runtime behavior.
