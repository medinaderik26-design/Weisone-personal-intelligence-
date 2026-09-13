# PI-028 — Provider Tokenizer Adapters

## Objective

Turn the PI-027 token-measurement boundary into a concrete adapter layer that can use real tokenizer implementations or provider-reported usage.

## Design

```text
Provider / Model
      ↓
Tokenizer Adapter
      ↓
TokenMeasurement
      ↓
Execution Evidence
      ↓
Resource Accounting
      ↓
Routing / Budget Decisions
```

### GenericTokenizerAdapter

Wraps an installed tokenizer implementation that exposes `count(text)` and records the result as a tokenizer-derived measurement.

### TiktokenAdapter

Provides an optional concrete adapter for OpenAI-compatible tokenization through `tiktoken`.

The dependency is optional. The system fails explicitly when the library is unavailable rather than estimating tokens from characters or words.

### Provider-reported usage

`provider_reported_measurement()` accepts explicit input/output/context token counts returned by a provider. Missing values remain unknown.

## Research integrity rules

- Never convert character counts into token counts.
- Never infer token usage from word counts.
- Never invent provider pricing from token counts.
- Preserve the tokenizer/model/provider source of every measurement.
- Unknown measurements remain unknown.
- A tokenizer count is a measurement, not proof of economic savings.

## Why this matters

The Personal Intelligence system is being designed around a real operational problem: AI capacity is finite. Requests can hit provider limits, context limits, cost limits, latency constraints, or local hardware limits.

PI-028 establishes the measurement boundary needed before the system can intelligently compare resource consumption across providers.

## Next step — PI-029

Build resource budgets around measured token usage, latency, cost, and task quality without treating any single metric as a substitute for the others.
