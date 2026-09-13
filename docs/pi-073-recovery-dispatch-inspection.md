# PI-073 — Recovery Dispatch Inspection

PI-073 connects the durable PI-072 scheduler acknowledgement boundary to recovery inspection.

## Recovery states

`no acknowledgement → resume handoff`

`claimed → resume handoff`

`handed_off → verify acceptance`

`accepted → continue`

The inspector is observational. It does not execute a recovery action, grant authorization, or claim external completion.

## Truth boundaries

- A dispatch claim proves that Weisone reserved a scheduler-facing action.
- A handoff acknowledgement proves the action was handed to the scheduler.
- An acceptance acknowledgement proves the scheduler accepted it.
- None of these proves that the provider executed the work.
- None of these proves that an external side effect occurred.
- External completion remains governed by the separate effect-verification boundary.

## Safety

A dispatch key is bound to its task. A key observed against another task is rejected rather than guessed.

## Architecture

`Durable Dispatch Claim → Durable Scheduler Ack → Recovery Dispatch Inspector → Recovery Boundary`

This gives restart recovery a deterministic observation point without allowing recovery logic to silently cross the execution or external-effect boundaries.

## Next step

PI-074 should create an explicit scheduler handoff/acceptance receipt that can be attached to the existing action ledger, making the scheduler boundary visible in the same durable evidence chain.
