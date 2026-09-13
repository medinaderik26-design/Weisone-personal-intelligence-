# PI-066 — Drift-Aware Recovery Execution Boundary

## Purpose

PI-066 connects PI-065 reconciliation policy to the scheduler boundary.

The system may inspect recovery state automatically, but ambiguous state must not silently become another external action.

## Flow

`Recovery Decision → Drift Policy → Execution Boundary → Scheduler Action`

### No drift / expected progression

The original scheduler recovery decision is allowed through.

### Recoverable divergence

The task is deferred for reinspection rather than immediately retried or rerouted.

### Human-review-required divergence

Automatic execution stops and the task is sent to human review.

## Safety boundary

The boundary does not execute work, grant authorization, or declare external success. It only determines whether a recovery decision is allowed to reach the scheduler.

This keeps recovery reasoning separate from execution authority.

## Next step

PI-067 should persist the boundary decision so every automatic recovery attempt has a durable record of the drift classification and resulting scheduler action.
