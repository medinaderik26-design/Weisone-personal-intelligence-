# PI-040 — Persistent Authorization History & Revocation Propagation

## Purpose

Make revocation effective beyond the process that originally received it.

A consent change should be visible to future workers, queued tasks, and execution boundaries rather than remaining trapped in one in-memory component.

## Core rule

**Revocation wins over previously granted consent.**

Once a matching revocation exists, a future execution check must deny the provider/task combination until a new explicit consent grant is established through the higher-level consent system.

## Architecture

`Consent → Authorization Decision → Queue/Worker → Revocation Guard → Execute`

Revocation path:

`Person → Revoke → Revocation Registry → Workers/Queues → Future execution denied`

## Why this matters

A personal intelligence may eventually have multiple workers, providers, local processes, queues, and long-running tasks. A permission model that only exists in one process is not sufficient.

## Safety boundary

PI-040 does not cancel an already-running external action automatically. It provides a check that can stop **future execution** and prevent queued work from starting after revocation. Long-running or externally committed operations require a separate cancellation/compensation protocol.

## Persistence

The current registry is a reference implementation. Production persistence should use the same contract with durable storage, authenticated propagation, timestamps/versioning, and recovery behavior.

## Next step

PI-041 should add **authorization versions / epochs**, allowing workers to detect that a permission decision became stale even when they received an older authorization record before revocation.
