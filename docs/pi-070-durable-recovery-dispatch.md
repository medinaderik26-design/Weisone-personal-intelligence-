# PI-070 — Durable Recovery Dispatch Idempotency

PI-069 prevents duplicate recovery dispatches during one process lifetime. PI-070 makes that protection survive process restarts.

## Dispatch identity

A scheduler-facing recovery action is identified by a deterministic key derived from:

`task_id + reconciliation classification + action`

The key is hashed before storage.

## Behavior

First claim:

`claim → stored → scheduler may receive the action`

Repeated claim after restart:

`claim → existing key → rejected`

A materially different recovery decision receives a different key and can be claimed independently.

## Safety

This is an idempotency boundary, not authorization. A successful claim proves only that the recovery action has not previously been claimed under the same dispatch identity.

The store contains metadata only and does not contain prompts, credentials, provider secrets, or sensitive payloads.

## Architecture

`Durable Boundary Decision → Durable Dispatch Claim → Scheduler`

The duplicate check now survives process crashes and database reopen.

## Next step

PI-071 should bind the dispatch claim to the scheduler acknowledgement so the system can distinguish **claimed**, **handed off**, and **accepted for execution** without conflating them.
