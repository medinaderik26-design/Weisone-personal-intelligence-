# PI-063 — Durable Recovery Snapshot Versioning

## Purpose

Persist recovery snapshots as immutable versions so process restarts do not erase the sequence of known recovery states.

## Version model

Each task receives a monotonically increasing snapshot version:

`task-1: v1 → v2 → v3 ...`

Snapshots are stored as records rather than overwritten in place.

## Why versioning matters

After repeated failures or restarts, Personal Intelligence can distinguish:
- what the system knew at an earlier recovery point
- what changed later
- which decision followed which state

This creates a temporal audit trail instead of a single mutable recovery state.

## Safety

Snapshot persistence does not establish external truth. It records the internally known state and decision context at a point in time.

The public reference implementation stores structured metadata only and does not persist user prompts, credentials, provider secrets, or other sensitive payloads.

## Architecture

`Work State + Ledger + Reconciliation → Recovery Snapshot → Versioned Durable Store → Recovery`

## Next step

PI-064 should add **snapshot comparison and drift detection**, allowing the system to identify exactly what changed between recovery versions before deciding what action is safe next.
