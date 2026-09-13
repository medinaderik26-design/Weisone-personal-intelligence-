# PI-086 — Durable Claim → Scheduler Handoff Boundary

## Purpose

PI-086 creates the explicit boundary between a durable recovery dispatch claim and scheduler handoff evidence.

```text
Policy Decision
      ↓
Policy Boundary
      ↓
PI-084 Dispatch Request
      ↓
PI-085 Durable Dispatch Claim
      ↓
PI-086 Handoff Request
      ↓
Scheduler Handoff Receipt
      ↓
Scheduler Acceptance
      ↓
Execution
      ↓
Provider Accepted
      ↓
Externally Confirmed
```

## Rules

- A scheduler handoff request requires a successful durable claim.
- A duplicate or blocked claim cannot create a new handoff.
- An execution intent ID is required at the handoff boundary.
- The handoff request does not call the scheduler.
- Recording `handed_off` is evidence that Weisone recorded the handoff boundary; it is not evidence that the scheduler accepted or executed the work.
- Scheduler acceptance remains a separate state.
- Provider acceptance remains a separate state.
- External completion remains a separate evidence boundary.

## Why the boundary matters

A durable claim proves that a specific logical recovery action has claimed its dispatch identity. Handoff is the next distinct fact: Weisone has recorded that the action crossed the scheduler handoff boundary.

These are deliberately separate because a process can crash between them. If they were collapsed, recovery could mistake an uncompleted handoff for a scheduler-accepted action and potentially duplicate work.

## Safety principle

> Never promote an internal state transition into evidence about an external system.

PI-086 preserves that rule by producing only a handoff request and a `handed_off` receipt. It does not infer scheduler acceptance, execution, provider acceptance, or external completion.
