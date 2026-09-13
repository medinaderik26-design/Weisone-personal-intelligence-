# PI-081 — Projection Drift Policy

PI-081 turns PI-080 descriptive projection drift into an explicit policy decision.

## Classifications

- **no_drift** → continue
- **expected_progression** → continue
- **identity_divergence** → human review
- **unexpected_divergence** → reinspect

## Expected progression

Changes limited to lifecycle stages/current stage are treated as normal progression.

A completion-evidence change accompanying lifecycle progression is also expected.

## Identity boundary

An execution-intent change is not treated as ordinary progress. It requires human review because execution identity is part of the evidence chain.

## Truth boundary

The policy does not decide that an external action succeeded. It only classifies changes in what Weisone's durable projection says it knows.

## Architecture

`Durable Projection → Drift Detector → Drift Policy → Recovery/Execution Boundary`

The policy remains separate from authorization and execution.

## Next step

PI-082 should durably record projection-drift policy decisions so recovery can explain not only what changed, but why Weisone continued, reinspected, or stopped.
