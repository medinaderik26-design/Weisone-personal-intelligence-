# PI-036 — Pre-Execution Authorization Gate

## Purpose

Create one final policy checkpoint before the Personal Intelligence allows a provider to execute work.

## Gate

`Identity/Permission → Provider Policy → Data Boundary → Privacy → Resource Budget → Execute`

PI-036 does not replace the existing permission, quota, scheduler, idempotency, or failover systems. It composes policy decisions into an explicit authorization result.

## Deny conditions

Execution is denied when:

- the provider has no registered policy
- provider policy rejects the task or sensitivity
- high-privacy data would cross a non-local boundary
- required data is outside the authorized sensitivity set
- an explicit resource budget is exceeded
- an external side effect is not authorized by the provider policy

## Design principle

A provider being available does **not** mean it is authorized.

A provider having capacity does **not** mean it may receive the data.

A task being technically executable does **not** mean it should execute.

The final gate exists to make those distinctions explicit before execution.

## Result

The gate returns an `AuthorizationDecision` containing:

- allowed/denied
- provider
- reasons for denial
- the minimized fields permitted to cross the boundary

## Next step

PI-037 should add an **audit trail for authorization decisions**, so the Personal Intelligence can explain what it allowed, what it denied, and why.
