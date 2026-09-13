# PI-074 — Scheduler Handoff and Acceptance Receipts

PI-074 adds a durable evidence record for the scheduler boundary and binds it to the execution intent.

## Boundary

`handed_off → accepted`

The receipt is tied to:

- task ID
- execution intent ID
- dispatch key
- scheduler state
- timestamp

The identity cannot change for an existing dispatch key.

## Meaning

**Handed off** means Weisone has evidence that the recovery action reached the scheduler boundary.

**Accepted** means the scheduler acknowledged acceptance.

Neither state proves that execution started, that a provider accepted the operation, or that an external side effect occurred.

## Durability

Receipts are stored in SQLite and survive process restart. Repeating the same receipt state is idempotent; moving backward is rejected.

## Evidence chain

`planned → confirmed → authorized → claimed → handed_off → accepted → executing → provider_accepted → externally_confirmed`

PI-074 establishes the scheduler portion of that chain without weakening the later execution and external-effect verification boundaries.

## Next step

PI-075 should bridge the scheduler receipt into the existing Action Ledger so the full lifecycle can be reconstructed from one durable evidence chain.
