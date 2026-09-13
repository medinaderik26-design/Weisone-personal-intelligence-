# PI-058 — Durable Action Ledger

## Purpose

Make the accountable action history survive process restarts while preserving PI-056 lifecycle and identity guarantees.

## Storage

The reference implementation uses local SQLite through Python's standard library.

It stores only ledger metadata:
- task ID
- execution intent ID
- operation
- target
- lifecycle stage
- statement
- timestamp
- optional evidence confidence

Sensitive prompts, message bodies, credentials, provider secrets, and raw personal memory are intentionally excluded.

## Recovery guarantee

A ledger can be closed, reopened, and queried without losing its recorded lifecycle history.

Every new append still passes through:

`Identity Check → Lifecycle Validator → Durable Write`

Therefore persistence does not weaken the safety boundary.

## Architecture

`Intent → Lifecycle Ledger → SQLite → Process Restart → Recoverable History`

## Production hardening still required

- encryption at rest where appropriate
- filesystem permissions
- retention/deletion policy
- corruption handling
- backup strategy
- access auditing
- migration/versioning

## Next step

PI-059 should add **ledger recovery/reconciliation**, allowing Personal Intelligence to inspect an interrupted action history and explicitly identify work that requires resume, retry, reroute, or human review.
