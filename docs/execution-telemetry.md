# PI-011 — Standardized Execution Telemetry

PI-011 defines the provider-neutral measurement record for one AI execution.

## Record

`ExecutionTelemetry` captures:

- task ID
- task type
- provider
- model
- success/failure
- latency when measured
- input tokens when actually reported/countable
- output tokens when actually reported/countable
- estimated cost when a defensible value is available
- quality when explicitly evaluated
- quality source/provenance

## Measurement rules

Unknown values remain `None`/unknown.

The system must not convert characters into tokens, infer cost from text length, or manufacture a quality score from a response merely because a response exists.

Quality measurements require provenance such as a human evaluator, benchmark, or explicit evaluation component.

## Architectural position

Telemetry sits between execution and feedback:

**Task → Router → Provider → Execution → Telemetry → Feedback → Performance History → Confidence → Future Routing**

This creates a standardized evidence surface without forcing the runtime to learn from every response.

## Why PI-011 matters

Personal Intelligence needs to know not only which provider answered, but what actually happened during the execution. That allows later measurement of resource pressure, reliability, latency, quality, and cost without confusing proxies with real metrics.

The next step is connecting this telemetry to the execution path through a modular adapter rather than rewriting the existing runtime in place.
