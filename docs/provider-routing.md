# Provider Routing

## PI-004

Personal Intelligence now treats provider availability and resource capacity as routing inputs.

The router currently applies these rules in order:

1. Ignore providers that report unavailable.
2. Ignore providers whose recorded request budget is exhausted.
3. For high-privacy tasks, prefer a provider named `local` when available.
4. Otherwise preserve deterministic provider ordering.

This is intentionally conservative. v0.1 does not claim intelligent optimization yet.

## Next Routing Signals

Future routing can incorporate measured:

- capability match
- actual tokenizer usage
- context-window pressure
- latency
- provider reliability
- cost per useful operation
- task quality
- privacy requirements
- local hardware capacity

The router should select from evidence, not assumptions.
