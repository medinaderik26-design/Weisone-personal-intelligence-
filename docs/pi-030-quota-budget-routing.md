# PI-030 — Quota + Resource-Budget Routing

## Purpose

PI-030 adds a pre-execution routing layer that combines:

- provider availability
- resource-manager request capacity
- explicitly reported quota windows
- task resource budgets
- measured task-specific performance confidence
- latency preference when measured

The router decides **where a task may run**. It does not execute the task.

## Preflight vs post-execution

Some resource facts can be known before execution; others cannot.

### Preflight facts

- known input-token count, when supplied by an actual tokenizer or provider
- configured budget limits
- known provider availability
- known request quota/capacity
- explicitly supplied cost estimate
- measured historical latency

### Post-execution facts

- actual output tokens
- actual total tokens
- actual provider-reported cost
- actual latency
- actual quality
- success/failure

PI-030 does **not** pretend that an output-token or cost limit can be guaranteed when the provider does not expose a hard preflight constraint.

## Decision flow

```text
Task
  ↓
Hard Eligibility
  ├─ Provider available?
  ├─ Resource capacity available?
  ├─ Quota exhausted?
  └─ Privacy boundary satisfied?
  ↓
Known Preflight Budget Checks
  ├─ Input tokens, if known
  ├─ Cost estimate, if explicitly known
  └─ Measured latency
  ↓
Measured Performance Ranking
  ├─ Reliable quality evidence
  ├─ Latency preference when requested
  └─ Remaining quota as a secondary signal
  ↓
Provider Selection
  ↓
Execution
  ↓
Actual Evidence / Accounting
```

## Safety rules

1. Unknown measurements remain unknown.
2. Characters and words are never converted into guessed token counts.
3. Cost is never inferred from text length.
4. Exhausted known quota is a hard exclusion.
5. High-privacy work is restricted to the local provider.
6. Sparse performance evidence does not receive a quality bonus.
7. Routing does not execute work or bypass permissions/idempotency boundaries.
8. Post-execution accounting remains authoritative for actual usage.

## Why this matters

The original problem was practical: a personal intelligence system may hit limits across multiple AI systems and accounts during real work.

PI-030 turns that pressure into an explicit control problem instead of treating model access as infinite.

The system can now reason about:

> **What can run, where it can run, and whether the known preflight resource requirements fit.**

## Current limitation

The budget evaluator currently treats unknown measurements conservatively by leaving them unknown rather than rejecting them. A provider integration that exposes hard context, token, cost, or quota limits can supply those facts before execution.

## Next step

PI-031 should establish provider-specific quota/reset adapters and make reset timing usable by the scheduler without inventing reset times.
