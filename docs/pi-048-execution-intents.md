# PI-048 — Execution Intent IDs

## Purpose

Bind a confirmed action plan to one specific execution intent so retries, workers, and routing changes cannot silently turn one approval into multiple unintended external actions.

## Model

`Action Plan → Human Confirmation → Execution Intent → Consume → Execute`

An execution intent contains:
- unique intent ID
- task ID
- scope ID
- exactly confirmed effects
- issuance timestamp
- consumed state

## One-shot boundary

An intent is issued once and can be consumed once.

A second attempt to consume the same intent is rejected. A worker must not create a new execution intent merely because an execution attempt failed; retry behavior must remain behind the existing idempotency and retry controls.

## Integrity checks

The intent can only be issued when:
- the action plan is valid
- confirmation task matches the plan task
- confirmed effects exactly match the plan effects

This prevents confirmation drift between preview and execution.

## Architecture

`Task → Scope → Plan → Preview → Confirmation → Intent ID → Authorization/Epoch/Revocation Checks → Idempotency → Execute → Evidence`

## Security

The intent contains authorization metadata, not the user's sensitive payload, credentials, or provider secrets.

## Next step

PI-049 should connect execution intents to the existing idempotency layer so the same intent remains the stable identity across safe retries and duplicate-delivery scenarios.
