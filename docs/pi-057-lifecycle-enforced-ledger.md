# PI-057 — Lifecycle-Enforced Action Ledger

## Purpose

PI-057 moves lifecycle validation from a caller responsibility into the ledger boundary itself.

PI-055 records accountable history. PI-056 defines valid state transitions. PI-057 makes every append pass through that lifecycle boundary.

## Guarantees

For one task:

- the execution intent cannot silently change
- the operation cannot silently change
- the target cannot silently change
- lifecycle stages must follow the registered transition graph
- impossible transitions are rejected before they become ledger history

Example:

`planned → confirmed → authorized → executing → provider_accepted → externally_confirmed`

is valid, while:

`planned → externally_confirmed`

is rejected.

## Architecture

`Action Event → Identity Check → Lifecycle Validator → Action Ledger`

The ledger remains append-only at the reference layer, but appends are now structurally constrained.

## Safety

This boundary does not grant authorization or prove external completion. It only guarantees that the recorded history is internally coherent.

## Next step

PI-058 should add **durable ledger persistence and recovery**, allowing the accountable action history to survive process restarts while preserving the same lifecycle guarantees.
