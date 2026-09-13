# PI-012 — Telemetry Adapter

PI-012 connects the standardized PI-011 telemetry record to the PI-010 execution feedback loop.

## Flow

**Execution → ExecutionTelemetry → Validation → TelemetryAdapter → ExecutionFeedbackLoop → TaskPerformanceRegistry**

The adapter deliberately passes only measured performance fields into the feedback system:

- provider
- task type
- success/failure
- quality when explicitly evaluated
- latency when measured

Other telemetry fields such as token counts and estimated cost remain available for future resource accounting without being silently converted into performance scores.

## Boundary

The adapter does not modify the existing runtime. This keeps the current execution path stable while providing a clean integration point for later runtime instrumentation.

It also does not make routing decisions. Routing remains downstream of the evidence and confidence layers.

## Safety rule

**Telemetry records facts. Feedback records observations. Confidence decides whether observations are strong enough to influence routing.**

This preserves the evidence-first architecture and prevents the Personal Intelligence layer from becoming an uncontrolled self-training loop.
