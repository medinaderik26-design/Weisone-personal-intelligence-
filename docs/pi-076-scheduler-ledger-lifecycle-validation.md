# PI-076 — Scheduler Ledger Lifecycle Validation

PI-076 prevents scheduler-derived ledger stages from bypassing earlier evidence boundaries.

## Required transitions

`authorized → handed_off → accepted`

A `handed_off` ledger stage requires prior authorization evidence.

An `accepted` ledger stage requires prior handoff evidence.

The validator rejects scheduler-derived stages when their required predecessors are absent.

## Why this matters

The ledger is an evidence narrative, not a place where the system may invent history after the fact. A scheduler receipt cannot retroactively authorize an action, and scheduler acceptance cannot imply that execution occurred.

## Boundary

The validator does not execute work, grant permission, or verify external effects. It only validates the sequence of evidence already recorded.

## Next step

PI-077 should integrate this validator directly into the scheduler-to-ledger bridge so invalid scheduler evidence cannot be appended through the normal bridge path.
