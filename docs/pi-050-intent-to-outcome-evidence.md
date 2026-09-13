# PI-050 — Intent-to-Outcome Evidence

## Purpose

Bind the user's confirmed execution intent to the measured execution evidence and the idempotency receipt.

This creates an accountability chain from authorization to actual outcome.

## Trace

`Human Confirmation → Execution Intent → Idempotency Key → Provider Execution → Telemetry + Resource Outcome → Execution Evidence → Final Receipt`

The trace must agree on the same task identity, and the intent ID must equal the idempotency execution key.

## Validation boundaries

A trace is rejected when:
- intent and telemetry task IDs differ
- intent and resource task IDs differ
- intent and receipt task IDs differ
- intent ID and execution key differ
- underlying execution evidence is invalid

## What this proves

It creates a structured record showing:
1. what logical action was approved
2. which execution identity was used
3. what provider/model executed it
4. what measurable resource outcome was observed
5. whether the execution succeeded

It does **not** by itself prove that an external side effect actually occurred. External systems may require their own confirmation or receipt.

## Architecture

`Action Scope → Action Plan → Confirmation → Execution Intent → Idempotency → Execution → Evidence → Receipt`

This is the first complete accountability spine for consequential Personal Intelligence actions.

## Next step

PI-051 should add an **external effect receipt boundary** so the system can distinguish internal execution success from verified completion in the external system.
