# PI-047 — Action Planning & Preview

## Purpose

Make consequential execution concrete before confirmation. The person should be able to see the exact effects that a confirmation will authorize.

## Action plan

An action plan binds:
- the existing action scope
- exact planned effects
- target of each effect
- human-readable description
- reversibility/compensation metadata

## Core rule

**Confirmation applies to the concrete plan, not an abstract permission.**

A plan cannot contain an effect outside its action scope.

## Example

```text
Scope:
  send_email → alice@example.com → send

Preview:
  send → alice@example.com:
  send the approved response

Confirmation:
  approved
```

A later attempt to add `delete`, change the target, or perform another operation must fail scope validation rather than silently expanding the confirmed action.

## Architecture

`Task → Action Scope → Action Plan → Preview → Human Confirmation → Authorization Receipt → Scope Guard → Execute`

## Safety

The preview layer describes intended effects. It does not execute them.

Confirmation does not bypass:
- consent
- provider policy
- data boundary
- permissions
- authorization epochs
- resource/quota limits
- idempotency
- side-effect safety

## Next step

PI-048 should introduce **Execution Intent IDs**, binding the confirmed plan to the exact execution attempt so retries cannot accidentally turn one confirmation into multiple unintended actions.
