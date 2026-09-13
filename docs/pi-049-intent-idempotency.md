# PI-049 — Execution Intent + Idempotency

## Purpose

Connect the confirmed execution intent to the existing idempotency registry so retries preserve one logical action identity.

## Core rule

**The execution intent ID is the idempotency key for the confirmed action.**

That means a retry does not create a new logical action. It reuses the same execution identity.

## Behavior

### No prior receipt

The intent is executable and its intent ID becomes the execution key.

### Successful prior receipt

Execution is blocked because the logical action already completed.

### Failed prior receipt

The same intent remains eligible for a retry, using the same execution key.

### Receipt/task mismatch

The system rejects the operation rather than allowing one intent to consume another task's execution history.

## Architecture

`Action Plan → Confirmation → Execution Intent → Intent/Idempotency Bridge → Provider Execution → Receipt`

Retry:

`Failed Receipt → Same Intent ID → Same Idempotency Key → Retry`

Duplicate delivery:

`Same Intent ID → Existing Successful Receipt → Do Not Execute Again`

## Important boundary

The bridge does not execute providers and does not decide whether an action is authorized. It connects two already-defined safety contracts:

- PI-048: what exact action the person approved.
- PI-019: whether that logical action has already completed.

## Next step

PI-050 should connect the intent/idempotency bridge to **execution evidence**, producing one traceable chain from confirmed human intent through provider execution and final measured outcome.
