# Correction — preamble marker current-owner association

## Purpose

Earlier #708 design notes treated `clearSingletonPreambleContribution()` calling `detachDeletedInstance(instance)` as an active third ownership channel alongside marker property metadata and opaque child provenance.

Source mechanics do show that marker cleanup can delete whatever DOM -> Fiber/props association currently exists on the persistent singleton.

However, the first public-API regression used a **synthetic marker arrangement** that real Fizz does not normally emit. This note narrows the conclusion.

## What remains true

Current HostSingleton hydration still eagerly binds the persistent singleton during complete work through `hydrateInstance()`.

`clearSingletonPreambleContribution()` has no old server HostSingleton Fiber token; its final `detachDeletedInstance(instance)` is broad.

A manually inserted marker can therefore detach an unrelated current body mapping if no later body acquisition occurs.

## What is no longer assumed

Real Fizz emits a body contribution marker because the body itself came from the Suspense/Activity boundary-local preamble.

When such a boundary is client-rendered:

- marker cleanup happens during mutation;
- the replacement client body HostSingleton is part of the new boundary tree;
- singleton acquisition can rebind the persistent body afterward.

Therefore a final event/props loss is not established merely from the helper's detach call.

## Active verifier

React PR 43 now runs a real-Fizz fallback-body takeover on **untouched source** and requires the replacement body's `onClick` to work after the boundary client-renders.

The old synthetic marker test is retained only as a contrast and is required to remain red.

Expected interpretation:

- real Fizz pass + synthetic fail -> no production current-owner symptom from this path; reject the no-detach source experiment;
- real Fizz fail -> current-owner association becomes a valid #708 repair lane again;
- verifier/preflight failure -> no semantic conclusion.

## Impact on marker descriptor design

Until the real-Fizz control executes, property descriptor work should **not** treat current-client Fiber/props preservation as a hard acceptance requirement derived from the synthetic test.

The strong #708 requirements remain:

1. remove only server-contributed singleton properties/style state;
2. preserve later imperative singleton state;
3. handle opaque body DSIH child ownership/provenance;
4. avoid raw DSIH/control-comment collisions;
5. keep adoption authority under review where reachable.

Normal HostSingleton release still needs its ordinary detach semantics.

## Disposition

**CORRECTED / FALSIFICATION PENDING.**

This note supersedes any earlier wording that treated current-client event association loss as already proven in a real Fizz lifecycle.
