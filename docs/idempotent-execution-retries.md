# PI-019 — Idempotent Execution + Retry Policy

## Purpose

Retries become dangerous when Personal Intelligence eventually operates external systems. A repeated request must not accidentally create two purchases, send two messages, duplicate a file operation, or perform another irreversible action twice.

## Idempotency

Each logical operation receives an `execution_key`. The `IdempotencyRegistry` records an `ExecutionReceipt` for that key.

If the same key is submitted again for the same task, the original receipt is returned rather than creating a second logical execution.

A key cannot be reassigned to another task.

## Retry policy

`RetryPolicy` distinguishes:

- successful execution — never retry
- non-retryable failure — stop
- retryable failure — retry until the attempt limit
- maximum attempts reached — stop

Retry delays use exponential backoff:

`base_delay × 2^(attempt − 1)`

## Safety boundary

This layer does not assume that every operation is safe to retry. A provider or tool integration must explicitly identify a failure as retryable.

For irreversible external actions, future integrations should require an idempotency key at the tool boundary before execution.

## Architecture

Task → Idempotency Check → Provider/Tool → Result → Receipt

Retryable failure → Backoff → Re-evaluate → Retry

Success → Receipt → Continuity / Evidence

## Principle

> A system that can retry work must first know how to retry it safely.

## Not yet solved

- persistent idempotency storage
- distributed locking
- crash recovery
- provider-specific retry classification
- transactional external-tool execution
- exactly-once semantics across network boundaries

Those remain future engineering problems rather than claims of completion.
