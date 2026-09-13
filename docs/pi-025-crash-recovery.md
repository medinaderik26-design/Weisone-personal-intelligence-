# PI-025 — Crash Recovery Engine

PI-025 connects the PI-020 durable work-state contract with the PI-024 execution lease system and the PI-022 recovery coordinator.

## Purpose

The system can now inspect unfinished work without blindly restarting it.

```text
Persistent WorkState
       ↓
Lease Inspection
       ↓
Is another worker still alive?
   ┌───┴────┐
  YES      NO
   ↓        ↓
 DEFER   Recovery Coordinator
             ↓
     Resume / Retry / Reroute /
     Defer / Human Review
```

## Safety behavior

- A live lease prevents reassignment of the task.
- An expired lease indicates that the previous owner is no longer maintaining execution.
- Expired liveness does **not** prove external completion or failure.
- Running work with unknown external completion remains a review/reroute decision.
- Queued work can resume when no active lease blocks it.
- The recovery engine inspects and recommends; it does not execute side effects.

## Why this matters

This creates the first explicit crash-recovery loop for Personal Intelligence. Work can survive a process failure while preserving uncertainty around real-world side effects.

The next layer can safely connect this inspection to a scheduler, provided execution continues to pass through permissions and idempotency controls.
