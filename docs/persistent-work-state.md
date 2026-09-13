# PI-020 — Persistent Work State

## Purpose

Personal Intelligence must not lose work merely because a process, provider, network connection, or machine session ends.

PI-020 defines a provider-neutral work-state contract and a replaceable storage boundary.

## State Model

A work item can move through:

`queued → running → completed`

or:

`queued → running → failed`

The state records task identity, attempt count, selected provider when known, the last error when applicable, a result reference when available, and metadata.

## Storage Boundary

The reference implementation uses `InMemoryWorkStateStore` so the contract can be tested without introducing a database dependency.

A future durable adapter can persist the same `WorkState` contract to local storage or another explicitly authorized store.

## Recovery Principle

On restart, the scheduler should be able to inspect unfinished work and decide whether it is safe to resume, retry, reroute, or require human intervention.

A `running` state must never be assumed to mean that external work definitely completed. External side effects require idempotency evidence before retry.

## Architecture

`Task → WorkState → Scheduler → Execution → Evidence → WorkState Update`

Recovery:

`Process Restart → Recover WorkState → Idempotency Check → Retry/Reroute/Intervention`

## Safety Rules

- Task IDs remain stable across retries.
- Attempt counts are explicit.
- Unknown completion state remains unknown.
- Persistence does not imply successful execution.
- Storage adapters must not silently broaden permissions.
- Personal data should not be persisted unless required and authorized.

## Next Step

PI-021 should provide a durable local storage adapter and crash-recovery tests while preserving the same storage contract.
