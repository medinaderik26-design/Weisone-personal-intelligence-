# PI-083 — Policy Execution Boundary

PI-083 establishes the boundary between recovery policy reasoning and execution.

## Flow

Projection → Drift → Policy Classification → Durable Policy Decision → Execution Boundary → Scheduler

## Rules

- `continue` may cross the boundary as a handoff decision.
- `reinspect` stops execution and requires fresh inspection.
- `human_review` stops execution.
- Unknown actions fail closed.
- A policy decision is not authorization.
- Crossing the boundary is not proof that execution occurred.
- The boundary does not authorize external side effects.

This preserves the distinction between **what Weisone decided** and **what Weisone was authorized or able to execute**.

The next layer can safely bind this boundary to scheduler handoff and durable dispatch evidence without allowing a recovery-policy record to become a credential.
