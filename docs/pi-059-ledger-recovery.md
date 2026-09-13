# PI-059 — Ledger Recovery & Reconciliation

## Purpose

Recover durable action history after a process restart without confusing internal execution state with external completion.

PI-058 provides durable ledger storage. PI-059 interprets the latest durable evidence and produces a recovery decision.

## Recovery decisions

- `complete` — external completion is already confirmed.
- `verify_external_effect` — execution/provider acceptance exists, but external completion must be verified before another attempt.
- `retry_or_reroute` — a prior attempt failed; existing retry and routing policies decide the next execution.
- `resume_or_defer` — work is incomplete and no external completion evidence exists.
- `human_review` — the recovered state is contradictory, missing required history, or otherwise unsafe to automate.

## Critical safety rule

A `running` task is **not** treated as failed merely because the process restarted.

Likewise, a `provider_accepted` entry is **not** treated as externally completed.

The recovery layer therefore refuses to blindly retry work whose external side effect may already have occurred.

## Architecture

`Durable Work State + Durable Action Ledger → Recovery Inspection → Evidence Check → Recovery Decision → Scheduler / Human Review`

Recovery does not execute the task itself.

## Reconciliation examples

### Confirmed completion

`provider_accepted → externally_confirmed`

Recovery can safely mark the logical task complete.

### Unknown external outcome

`executing → process crash`

Recovery requires verification before retrying.

### Provider accepted, external result unknown

`provider_accepted → verify_external_effect`

The system must establish what actually happened before creating another external side effect.

### Failed attempt

`failed → retry_or_reroute`

The existing idempotency, retry, resource, quota, authorization, and routing layers remain responsible for the actual next decision.

## Next step

PI-060 should add a **reconciliation record** that explicitly captures the relationship between recovered work state, ledger evidence, and the final recovery decision for auditability.
