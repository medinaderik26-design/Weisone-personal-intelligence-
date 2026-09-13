# PI-069 — Recovery Dispatch Idempotency

PI-069 prevents a recovery decision from being handed to the scheduler twice by the same logical recovery path.

## Dispatch identity

A recovery dispatch is identified by:

- task ID
- reconciliation classification
- recovery action

The dispatch must also reference the authoritative PI-068 boundary record.

## Behavior

`claim(key, boundary_record_id)` returns:

- `True` when the logical recovery decision has not been dispatched yet.
- `False` when the same decision was already claimed.

Different actions remain distinct decisions. For example, `reinspect` and `human_review` are not treated as duplicates.

## Safety boundary

This guard prevents duplicate scheduler handoff. It does **not** claim that the external operation completed successfully.

The durable boundary record remains the evidence for what decision was authorized for scheduler handoff; execution and external-effect verification remain separate concerns.

## Next step

PI-070 should make the dispatch guard itself durable so duplicate protection survives a process restart rather than existing only in memory.
