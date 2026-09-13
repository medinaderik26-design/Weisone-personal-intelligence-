# PI-072 — Durable Dispatch Acknowledgement

PI-071 separated claimed, handed-off, and accepted states. PI-072 makes those states durable across process restarts.

## State machine

`claimed → handed_off → accepted`

The state may not move backward.

Repeated writes of the same state are idempotent.

## Recovery behavior

After restart, the system can inspect the durable dispatch key and recover the last known scheduler boundary without guessing.

Examples:

- `claimed` → the dispatch was claimed, but handoff is not confirmed.
- `handed_off` → the action was handed to the scheduler, but scheduler acceptance is not confirmed.
- `accepted` → the scheduler accepted the action.

None of these states means the external action completed.

## Safety

The acknowledgement store records metadata only. It does not store prompts, credentials, provider secrets, or sensitive payloads.

## Architecture

`Durable Dispatch Claim → Durable Acknowledgement → Scheduler/Execution`

This closes another restart ambiguity while preserving the distinction between scheduler acceptance and external completion.

## Next step

PI-073 should connect the durable acknowledgement state to recovery inspection so restart recovery can automatically determine whether to resume handoff, verify scheduler acceptance, or stop for human review.
