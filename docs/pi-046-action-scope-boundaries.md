# PI-046 — Action Scope & Transaction Boundaries

## Purpose

Ensure that human confirmation and authorization apply only to the exact action the person intended.

## Scope model

An action scope binds:

- task ID
- operation
- target
- purpose
- explicitly allowed effects
- optional confirmation requirement
- optional scope identifier

## Core rule

**Authorization is not transferable to a broader action.**

A worker must match the requested operation, target, and effect against the original scope before execution.

## Example

A confirmation for:

`send_email → alice@example.com → send`

must not authorize:

`send_email → bob@example.com`

or:

`send_email → alice@example.com → delete`

or:

`create_calendar_event → alice@example.com`.

## Architecture

`Task → Action Scope → Confirmation → Authorization Receipt → Scope Guard → Execute`

## Why this matters

As the Personal Intelligence gains access to more tools, one broad permission becomes dangerous. Scope boundaries prevent permission expansion through chained tools, retries, routing changes, or worker behavior.

## Safety

The scope guard does not grant permission by itself. It is one constraint in the existing authorization chain. Consent, provider policy, data boundaries, permissions, resource limits, and confirmation requirements still apply.

## Next step

PI-047 should introduce **Action Planning & Preview**, allowing the Personal Intelligence to show the exact proposed effects before consequential execution and obtain confirmation against that concrete plan.
