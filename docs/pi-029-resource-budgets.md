# PI-029 — Resource Budgets

## Purpose

Personal Intelligence needs an explicit way to represent how much resource a task is allowed to consume.

PI-029 introduces a provider-neutral budget boundary for measured:

- input tokens
- output tokens
- total tokens
- cost
- latency

## Safety rule

A missing measurement remains unknown. The evaluator does not convert characters or words into tokens and does not infer cost from text length.

## Decision model

```text
Task
  ↓
Resource Budget
  ↓
Measured Usage
  ↓
Budget Evaluation
  ↓
Allow / Reject
```

This is deliberately separate from provider routing. Routing decides *where* work may run; budgeting defines *how much resource* the work may consume.

## Important limitation

The current evaluator only rejects when a known measurement exceeds an explicit limit. Unknown usage is not treated as an invented zero and is not converted into an estimate.

## Next step

PI-030 should connect budget evaluation to provider selection and quota windows so Personal Intelligence can choose an eligible provider before execution rather than discovering resource limits afterward.
