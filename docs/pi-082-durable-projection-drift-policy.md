# PI-082 — Durable Projection Drift Policy

## Purpose

PI-082 makes the PI-081 projection-drift classification durable across process restarts.

The system now preserves not only what changed between lifecycle projections, but the policy decision made in response to that change.

## Evidence chain

`Projection vN → Projection Drift → Policy Decision → Durable Policy Record`

The record captures:

- task identity
- drift classification
- resulting action
- reason
- UTC timestamp

## Policy meanings

- `no_drift` → `continue`
- `expected_progression` → `continue`
- `unexpected_divergence` → `reinspect`
- `identity_divergence` → `human_review`

These classifications are policy judgments, not claims about external reality.

## Restart behavior

Policy decisions are persisted in SQLite and remain available after the process restarts. Records are append-only and ordered by insertion ID.

A later recovery process can therefore answer:

1. What projection was being evaluated?
2. What drift was observed?
3. How did policy classify it?
4. What action did policy recommend?
5. When was that decision recorded?

## Truth boundary

Durable policy evidence does **not** prove that the recommended action was executed.

It does not prove:

- scheduler execution
- provider acceptance
- external completion
- successful external side effects

Those remain separate evidence boundaries.

## Safety principle

> Preserve the decision without confusing the decision with the outcome.

PI-082 is therefore an accountability layer, not an execution layer.

## Next step

PI-083 should connect the durable policy decision to the existing recovery/execution boundary without allowing a policy record to authorize execution by itself.
