# Upstream issue draft

Status: `hold — existing issue #15430 already owns the primary report`

Do not post without explicit authorization.

## Proposed title

`streamText explicit abort can wait on callbacks or provider cancellation after terminal selection`

## Draft

An explicit caller abort should become the single terminal outcome for `streamText`, including while a provider read remains pending or a provider stream has been created but has not yet been registered with the internal stream owner.

The existing report in #15430 and candidate PR #16852 cover the primary hang where `result.text` and `result.steps` remain pending after the caller signal fires. Additional target-native characterization identifies three narrower lifecycle requirements:

1. `onAbort` and telemetry callback completion must not delay root-result rejection, outward abort publication, stream closure, or provider cancellation.
2. A provider value or ordinary provider error arriving after caller abort must yield to the already-selected abort outcome.
3. A provider stream returned after abort but before internal registration must receive a direct cancellation request, and a rejecting or never-settling provider `cancel()` must not keep public state or the internal setup task pending.

Expected behavior:

- root result promises reject once with the caller abort reason;
- derived getters settle through those roots;
- each active consumer receives one abort part;
- `onAbort` runs once;
- later provider values/errors do not claim a competing terminal outcome;
- provider cancellation is requested without granting a provider-controlled cancellation promise authority over public settlement;
- ordinary reader cancellation remains consumer-scoped;
- already committed external tool effects are reported truthfully and are not represented as reversed.

Suggested tests:

- pending `onAbort` callback;
- provider error immediately after caller abort;
- multiple active consumers;
- provider stream returned during the registration gap;
- direct provider `cancel()` rejection;
- direct provider `cancel()` that never settles;
- listener, reader, timer, and unhandled-rejection cleanup;
- ordinary consumer cancellation negative control.

## Posting decision

Prefer commenting on or revising the existing issue/PR only after maintainer direction. A new issue would duplicate the main report unless maintainers want the narrower cancellation-promise problem split out.