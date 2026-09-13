# PI-075 — Scheduler Evidence in the Action Ledger

PI-075 bridges durable scheduler receipts into the Action Ledger so scheduler evidence participates in the same lifecycle record.

## Evidence chain

`planned → confirmed → authorized → claimed → handed_off → accepted → executing → provider_accepted → externally_confirmed`

Scheduler receipts now produce ledger evidence at `handed_off` and `accepted`.

## Truth boundary

The bridge records what the scheduler acknowledged. It does not infer that execution started or that an external side effect occurred.

An `accepted` ledger entry explicitly states that execution outcome remains unconfirmed.

## Design rule

The ledger remains the authoritative narrative of the action lifecycle, while scheduler receipts remain the durable source evidence for the scheduler boundary.

The bridge is deliberately one-way: scheduler evidence can be represented in the ledger, but the ledger cannot manufacture a scheduler acknowledgement.

## Next step

PI-076 should make the bridge lifecycle-aware, validating that scheduler-derived ledger stages can only appear after the appropriate prior ledger stages and cannot bypass authorization or confirmation boundaries.
