# PI-027 — Actual Token Measurement

PI-027 creates the measurement boundary needed to distinguish real token usage from text-length proxies.

## Contract

```text
Prompt
  ↓
Actual tokenizer OR provider-reported usage
  ↓
TokenMeasurement
  ↓
Execution accounting
  ↓
Resource-aware decisions
```

Supported measurements:
- input tokens
- output tokens
- context tokens
- measurement source

Measurement sources are explicitly classified as:
- `tokenizer`
- `provider_reported`
- `unknown`

## Research integrity rule

Character count is not token count.

Word count is not token count.

A character-budget experiment such as GX-012-B can demonstrate behavior under a shrinking character budget, but it cannot by itself establish token savings, compute savings, cost savings, or energy savings.

PI-027 therefore accepts only an actual tokenizer count or a provider-reported usage count as evidence of token usage.

## Next step

Add provider/model-specific tokenizer adapters and capture input/output/context counts during controlled benchmark runs. Keep model, prompt, quality evaluation, and other experimental conditions fixed so resource changes can be compared without confusing measurement proxies with causal effects.
