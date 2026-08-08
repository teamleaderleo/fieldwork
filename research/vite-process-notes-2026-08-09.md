# Vite workflow notes — 2026-08-09

These notes capture process lessons from the current Vite correctness lane. They are observations about how the research has worked well, not Vite-specific requirements for every future campaign.

## What has been working

### Start from observed friction when possible

Several of the strongest candidates were not found by scanning for suspicious code. They surfaced while validating another change: an unexpected rebuild, a close that did not settle, or state that changed across restart. Following the observed anomaly back to its owner produced clearer questions than beginning with a guessed patch.

### Build the ownership model before the patch

The productive recurring questions have been:

- Who created this resource or state?
- Which lifetime owns it?
- What operation transfers or ends that ownership?
- What should completion mean at this boundary?
- What happens on success, error, cancellation, restart, warm state, and cold state?

This has been especially effective around plugin containers, Rolldown bundles, dependency-optimizer metadata, watchers, and server generations.

### Require a native FAIL before promoting a candidate

Source review has generated useful hypotheses, but the reliable promotion point has been a target-native regression that fails on the relevant clean baseline. This prevents plausible-looking lifetime theories from becoming candidate bugs without evidence.

Invalid probes are also useful when retained honestly. In the pre-init optimizer work, a middleware-mode probe accidentally initialized the optimizer too early and therefore answered the wrong question. Recording why it was invalid made the corrected create-before-listen regression stronger.

### Use one finding to probe adjacent branches, but make each branch earn promotion

Once an invariant is understood, neighboring cases become cheap to formulate. Warm-cache metadata replacement suggested checking cold initialization; failed restart construction suggested checking initial construction failure. This is productive as long as each neighboring case is independently reproduced instead of being assumed from code similarity.

### Distinguish candidate failure from CI noise

Broad CI has been most useful when interpreted rather than treated as a binary badge. The current lane has seen:

- target regressions that correctly fail on baseline;
- unrelated product-test failures that pass on exact rerun;
- platform failures that disappear on the unchanged candidate;
- formatting-only failures after the product matrix was green.

Classifying those separately avoids rewriting good code in response to unrelated noise while still preserving the original failure receipt.

### Separate research history from submission shape

Exploration benefits from explicit baseline branches, experiment carriers, temporary tests, and detailed Fieldwork notes. Review benefits from the opposite: one minimal commit, the native regression, the repair, and a short explanation of the governing invariant.

Keeping a clean hold-ready branch after the evidence stabilizes has worked well. The research record remains available without forcing maintainers to review the research process itself.

## Current working loop

```text
real anomaly or source-grounded question
        ↓
plain-language state/ownership model
        ↓
small target-native probe
        ↓
clean baseline FAIL
        ↓
minimal repair
        ↓
focused PASS
        ↓
adjacent boundary probes
        ↓
full relevant CI / platform check
        ↓
clean hold-ready commit
        ↓
human-controlled upstream pacing
```

The important part is not the exact sequence. The useful property is that every promotion step has an explicit piece of evidence and a way to stop when the hypothesis is wrong.

## Positive consequence

The lane is producing more than patches. Repeatedly explaining object identity, shallow copies, plugin lifecycles, async settlement, metadata replacement, restart generations, and ownership boundaries is building a reusable mental model of JavaScript/TypeScript systems work. That learning appears to improve subsequent source review: code that initially looked like incidental implementation detail becomes easier to evaluate in terms of lifetime, identity, and authority.

The current submission bottleneck is intentionally human pacing rather than research throughput. That is healthy: research can continue, candidates can be hardened and frozen, and upstream review can remain measured.
