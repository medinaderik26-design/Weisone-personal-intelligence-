# PI-056 — Action Ledger Lifecycle Validation

## Purpose

PI-055 created an accountable action history. PI-056 makes that history state-aware so impossible or contradictory transitions are rejected.

## Lifecycle

Typical path:

`planned → confirmed → authorized → executing → provider_accepted → externally_confirmed`

Failure/recovery paths are explicit:

`executing → failed → retrying → executing`

`failed → rerouted → executing`

`failed → human_review`

Cancellation and deferral are also explicit states.

## Safety rule

Terminal states cannot silently move backward.

For example:

- `externally_confirmed → planned` is rejected.
- `cancelled → executing` is rejected.
- unknown stages are rejected.

The validator only governs ledger state transitions. It does not execute actions, grant authorization, or determine whether external evidence is truthful.

## Architecture

`Action Ledger → Lifecycle Validator → Valid Event / Rejected Event`

This preserves a coherent history that can be inspected later instead of allowing the ledger to become an internally contradictory narrative.

## Next step

PI-057 should connect lifecycle validation to **ledger event append operations**, so invalid transitions are blocked at the ledger boundary rather than requiring callers to validate them manually.
