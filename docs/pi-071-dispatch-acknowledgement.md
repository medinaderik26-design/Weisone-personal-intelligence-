# PI-071 — Recovery Dispatch Acknowledgement

PI-071 separates three states that must never be conflated:

1. **Claimed** — Weisone reserved the dispatch identity.
2. **Handed off** — the recovery action was passed to the scheduler boundary.
3. **Accepted** — the scheduler explicitly acknowledged acceptance for execution.

## Transition rule

`claimed → handed_off → accepted`

Transitions cannot skip states or move backward.

## Safety

A dispatch claim does not prove handoff.

A handoff does not prove scheduler acceptance.

Scheduler acceptance does not prove the external action completed.

That preserves the evidence chain:

`claim → handoff → scheduler acceptance → execution → provider acceptance → external confirmation`

Each stage needs its own evidence.

## Next step

PI-072 should make acknowledgement state durable and idempotent, so restart recovery can determine the last confirmed scheduler boundary without guessing.
