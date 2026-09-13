# PI-017 — Quota Windows

Personal Intelligence needs to know not only whether a provider is available, but whether its reported capacity is exhausted and, when known, when that capacity resets.

## Model

`QuotaWindow` records provider-reported facts:

- provider
- remaining requests
- request limit
- reset timestamp

Unknown values remain unknown.

## Safety rules

1. Never invent a quota limit.
2. Never invent a reset time.
3. Never convert characters into tokens.
4. An explicitly exhausted provider is not eligible for new work.
5. An unknown quota does not automatically mean exhausted.
6. Reset information is descriptive until a scheduler uses it.

## Why this matters

The practical problem is repeated daily capacity pressure across multiple AI systems and accounts. A resource-aware intelligence layer should eventually be able to answer:

> Which provider can perform this task now, and which capacity should be preserved for later?

PI-017 establishes the factual quota boundary without yet making scheduling decisions.

## Next layer

PI-018 can build an execution queue around this model:

`Task → Eligibility → Quota Check → Execute / Defer → Retry / Fallback`

The queue should preserve task identity and continuity while avoiding uncontrolled retries or duplicate work.
