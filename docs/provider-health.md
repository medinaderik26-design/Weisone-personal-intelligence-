# Provider Health

PI-007 introduces measured provider history without pretending that quality can be inferred automatically.

Tracked signals:

- successes
- failures
- success rate
- optional quality scores
- optional latency measurements

Quality is intentionally an input to the registry rather than an invented score. A future evaluation layer can produce quality measurements for specific task classes.

The router should eventually consider provider health only when enough observations exist. Unknown quality is not the same as poor quality.

Future work:

- task-specific quality history
- confidence/sample counts
- rolling windows
- provider outage detection
- model-specific health
- evaluator integration
- quality/cost tradeoff measurement
