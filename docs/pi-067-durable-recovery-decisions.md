# PI-067 — Durable Recovery Decisions

PI-066 establishes the execution boundary for recovery decisions. PI-067 makes those decisions durable.

## What is recorded

Each recovery-boundary decision records:

- task ID
- drift/reconciliation classification
- action selected
- reason
- timestamp

The durable record contains decision metadata only. It does not store prompts, credentials, provider secrets, or sensitive payloads.

## Why this matters

After a crash or restart, Weisone can answer:

> What recovery decision did the system make, and why?

The decision log is evidence of the system's reasoning boundary. It is not proof that an external action completed.

## Architecture

`Recovery Snapshot → Drift → Reconciliation → Execution Boundary → Durable Decision Log`

This gives recovery decisions a durable audit trail without turning the audit record into a copy of the user's private data.

## Next step

PI-068 should connect the durable decision log to the execution boundary itself, creating one authoritative recovery record per decision before the scheduler receives the action.
