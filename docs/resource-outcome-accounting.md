# PI-013 — Resource Outcome Accounting

PI-013 adds a provider-neutral ledger for measured resource outcomes.

## What is recorded

Each `ResourceOutcome` may contain:

- provider
- task ID
- actual input tokens, when available
- actual output tokens, when available
- measured latency
- defensible cost

The registry can aggregate known costs and known total tokens by provider.

## Evidence boundary

Unknown measurements stay unknown.

The registry does **not**:

- convert characters into tokens
- estimate tokens from response length
- invent provider pricing
- treat a missing cost as zero
- treat missing token counts as zero
- infer efficiency from a proxy measurement

A zero cost is therefore a meaningful recorded value, while an unknown cost remains `None`.

## Architectural position

**Execution → Telemetry → Resource Outcome → Feedback → Performance History → Routing**

This gives Personal Intelligence a factual resource ledger that can eventually support quota management, provider comparison, budget controls, and resource-aware routing.

## Why this matters

The system is intended to operate across multiple AI providers and local models. Resource pressure is therefore part of the intelligence problem itself. Before PI can optimize resources, it needs a trustworthy record of what resources were actually consumed.

## Next step

PI-014 should connect resource outcomes to the telemetry adapter and establish a single execution evidence object without modifying the stable runtime directly.
