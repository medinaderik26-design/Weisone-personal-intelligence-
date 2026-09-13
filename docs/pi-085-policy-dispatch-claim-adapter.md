# PI-085 — Durable Policy Dispatch Claim Adapter

## Purpose

PI-085 connects the PI-084 policy dispatch boundary to the existing PI-070 durable recovery dispatch store.

It answers:

> Has this policy-approved recovery action been durably claimed for scheduler handoff?

It does **not** execute the task, authorize external side effects, or prove scheduler acceptance or external completion.

## Evidence chain

```text
Recovery Snapshot
      ↓
Projection Drift
      ↓
Policy Classification
      ↓
Durable Policy Decision
      ↓
Policy Execution Boundary
      ↓
Policy Dispatch Bridge       ← PI-084
      ↓
Durable Dispatch Claim       ← PI-085
      ↓
Scheduler Acknowledgement
      ↓
Execution
      ↓
Provider Accepted
      ↓
Externally Confirmed
```

## Behavior

1. A policy dispatch request must be explicitly eligible.
2. The request must contain a deterministic dispatch key.
3. The adapter asks the durable SQLite dispatch store to claim the action.
4. The first claim succeeds.
5. A duplicate logical recovery action returns an idempotent non-claim result.
6. The claim survives process restart because PI-070 persists it.
7. The adapter verifies that the durable claim key matches the policy request key.

## Boundary discipline

The adapter does not:

- authorize the action
- call a provider
- call the scheduler
- retry execution
- infer execution from a claim
- infer provider acceptance from a claim
- infer external completion from a claim

A durable claim means only:

> Weisone has durably recorded that this specific policy-approved recovery action has claimed its scheduler dispatch identity.

It does not mean the scheduler received it, accepted it, executed it, or caused an external effect.

## Restart safety

PI-070 stores the dispatch key with a uniqueness constraint. A repeated claim for the same task/classification/action therefore resolves to the existing logical action rather than creating another claim.

This gives Weisone a durable idempotency boundary without pretending that idempotency is authorization or completion evidence.
