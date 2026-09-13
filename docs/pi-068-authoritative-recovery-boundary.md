# PI-068 — Authoritative Recovery Boundary

PI-068 makes the execution-boundary decision itself durable.

## Rule

Before the scheduler receives a recovery action, the system records the decision that crossed the execution boundary.

The durable record contains:

- task ID
- reconciliation classification
- selected action
- reason
- boundary identity
- timestamp

## Why this is different from PI-067

PI-067 records recovery decisions generally.

PI-068 identifies the **authoritative boundary event**: the specific decision that was accepted for scheduler-facing recovery.

This creates a clean audit chain:

`Recovery Snapshot → Drift → Reconciliation → Boundary Decision → Scheduler`

## Safety

The boundary record is not authorization and is not evidence that an external effect occurred. It proves only that Weisone recorded a specific recovery decision before handing that decision to the scheduler.

Sensitive payloads, prompts, credentials, and provider secrets remain outside the ledger.

## Next step

PI-069 should add duplicate-boundary protection so the same recovery decision cannot accidentally be handed to the scheduler twice after a restart.
