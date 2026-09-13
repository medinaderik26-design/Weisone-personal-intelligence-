# PI-077 — Lifecycle-Aware Scheduler-to-Ledger Bridge

PI-077 integrates the PI-076 lifecycle validator directly into the scheduler-to-ledger path.

## Enforced path

`authorized → handed_off → accepted`

The bridge receives the prior ledger stages and refuses to create scheduler-derived evidence when the required predecessor is absent.

## Guarantees

- A scheduler handoff cannot create an implied authorization.
- Scheduler acceptance cannot appear without a recorded handoff.
- The bridge remains observational and does not execute work.
- Scheduler acceptance still does not prove execution started, provider acceptance, or external completion.
- The ledger entry carries the original task ID and execution intent ID from the scheduler receipt.

## Evidence boundary

The resulting architecture keeps the distinction between:

**authorization → scheduler handoff → scheduler acceptance → execution → provider acceptance → external confirmation**

Each boundary must produce its own evidence.

## Next step

PI-078 should add a durable end-to-end lifecycle projection that reconstructs the complete evidence chain for a task without conflating scheduler acceptance with execution success.
