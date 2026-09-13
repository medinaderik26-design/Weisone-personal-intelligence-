# PI-061 — Durable Reconciliation History

## Purpose

Persist recovery decisions so the explanation of what happened during an interruption survives process restarts.

PI-060 defined the reconciliation record. PI-061 gives it a durable local storage boundary.

## Stored record

Each record preserves:
- task ID
- execution intent ID when known
- prior work status
- latest ledger stage
- recovery action
- reason
- timestamp

## Recovery chain

`Durable Work State → Action Ledger → Recovery Decision → Reconciliation Record → Durable Reconciliation Log`

After restart, Personal Intelligence can reconstruct not only what work was unfinished, but why a particular recovery decision was made.

## Safety

The database stores decision metadata, not prompts, message bodies, credentials, provider secrets, or other sensitive payloads.

Durability does not mean correctness. A persisted recovery decision is still only a record of what the system decided at that time.

## Next step

PI-062 should unify the durable work state, action ledger, and reconciliation history behind a single **recovery snapshot**, making crash recovery deterministic and easier to audit.
