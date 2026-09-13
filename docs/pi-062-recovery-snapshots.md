# PI-062 — Unified Recovery Snapshots

## Purpose

PI-062 creates one validated object representing the state of a task at recovery time.

Instead of asking separate components what happened, recovery can inspect one snapshot containing:
- durable work state
- latest action-ledger evidence
- latest reconciliation record
- current recovery decision

## Architecture

`Work State + Action Ledger + Reconciliation History → Recovery Snapshot → Recovery/Scheduler`

## Integrity rules

The snapshot rejects mismatched task identities between its components.

This prevents a recovery decision for one task from being accidentally paired with ledger or reconciliation evidence belonging to another task.

## Important boundary

A snapshot is a **consistent description of known state**, not proof that the external world matches that state.

External-effect verification remains a separate requirement.

## Next step

PI-063 should add **snapshot persistence/versioning**, allowing recovery snapshots to be stored atomically and compared across restarts.
