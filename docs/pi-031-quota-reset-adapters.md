# PI-031 — Provider Quota/Reset Adapters

## Purpose

Normalize provider-reported quota information into the Personal Intelligence quota model.

## Contract

Provider-specific adapters may report:

- provider name
- remaining request capacity
- request limit
- explicit reset timestamp

The adapter stores those facts in `QuotaRegistry` through `QuotaWindow`.

## Safety rules

- Never infer a reset time.
- Never infer quota from character counts, words, or estimated tokens.
- Unknown remaining capacity stays unknown.
- Unknown reset time stays unknown.
- A quota adapter reports facts; it does not decide whether a task is valuable.
- Provider credentials remain outside this repository's source code.

## Architecture

`Provider API → QuotaSource → QuotaAdapter → QuotaRegistry → BudgetAwareRouter`

## Why this matters

The Personal Intelligence layer needs to know not only which model is capable of a task, but whether that provider currently has usable capacity. Explicit reset timestamps also allow a future scheduler to defer work instead of repeatedly retrying an exhausted provider.

## Current implementation

`StaticQuotaSource` provides a deterministic local/test implementation. Real provider integrations can implement the same `QuotaSource` protocol later.

## Next step

PI-032 should add **quota-aware scheduling**: when a provider is exhausted but has a known future reset, the scheduler can defer eligible work until that window instead of treating the provider as permanently unavailable.
