# Upstream issue draft

Status: `hold — existing issue #15430 already owns the primary report`

Do not post without explicit authorization.

## Proposed title

`streamText explicit abort terminal mechanics can wait on observability or lose arbitration`

## Draft

An explicit caller abort should become the single terminal outcome for `streamText`, including while a provider read remains pending or a provider stream has been created but has not yet been registered with the internal stream owner.

The existing report in #15430 and candidate PR #16852 cover the primary hang where `result.text` and `result.steps` remain pending after the caller signal fires. Additional target-native characterization identifies three narrower lifecycle requirements:

1. `onAbort` and telemetry callback completion must not delay root-result rejection, outward abort publication, stream closure, or the provider cancellation request.
2. A provider value or ordinary provider error arriving after caller abort must yield to the already-selected abort outcome.
3. A provider stream returned after abort but before internal registration must receive a direct cancellation request.

Expected behavior:

- root result promises reject once with the caller abort reason;
- derived getters settle through those roots;
- each active consumer receives one abort part;
- `onAbort` runs once;
- later provider values/errors do not claim a competing terminal outcome;
- provider cancellation is requested during the registration gap;
- ordinary reader cancellation remains consumer-scoped;
- already committed external tool effects are reported truthfully and are never represented as reversed.

The stream returned by `streamLanguageModelCall()` has request-level cancellation settlement at the reviewed revision. Native Web Streams modeling and a target-native regression show that its outer `cancel()` promise settles after forwarding cancellation while provider cleanup remains pending, and provider cleanup rejection is contained. This result removes the earlier proposed sub-issue about a hostile provider-controlled cancellation promise retaining setup.

Suggested tests:

- pending `onAbort` callback;
- provider error immediately after caller abort;
- multiple active consumers;
- provider stream returned during the registration gap;
- model-call cancellation while provider cleanup remains pending;
- model-call cancellation when provider cleanup rejects;
- listener, reader, timer, and unhandled-rejection cleanup;
- ordinary consumer cancellation negative control.

## Posting decision

Prefer commenting on or revising the existing issue/PR only after maintainer direction. A new issue would duplicate the main report. The cancellation-promise investigation produced a negative result rather than a separate defect.
