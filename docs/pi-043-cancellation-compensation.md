# PI-043 — Safe Cancellation & Compensation

## Purpose

Define what the Personal Intelligence should do when authorization is revoked after work has started.

## Core distinction

**Cancellation is not the same as compensation.**

- Cancellation stops work that can still safely stop.
- Compensation is a separate, registered action intended to reverse or mitigate an already-committed external effect.
- Some effects cannot be safely reversed and require human review.

## Decision model

`Started? → Revoked? → Cancelable? → Compensation available? → Cancel / Compensate / Continue / Human Review`

## Outcomes

### Cancel before start
Queued work that has not started can be removed without external side effects.

### Cancel
Started work may be stopped when the operation explicitly supports safe cancellation.

### Compensate
If an external side effect has already occurred and a known compensation action exists, the system can schedule the registered compensation workflow.

### Human review
If an action is non-cancelable and cannot be safely compensated, the system must not invent a reversal. It escalates for review.

### Continue
If no cancellation condition is active, normal execution continues.

## Safety principle

The Personal Intelligence must never claim that an external action was reversed merely because it requested cancellation. Cancellation and compensation require their own execution evidence.

## Architecture

`Authorization Receipt → Execution → Side-Effect State → Cancellation Policy → Cancel / Compensate / Human Review → Evidence`

## Next step

PI-044 should introduce a **Side-Effect Registry**, describing which operations are reversible, cancelable, compensatable, or irreversible before the intelligence is allowed to perform them.
