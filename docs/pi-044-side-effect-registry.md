# PI-044 — Side-Effect Registry

## Purpose

Give the Personal Intelligence an explicit safety description for every external operation before it is allowed to execute.

## Side-effect classes

Each registered operation declares whether it is:

- **Cancelable** — can be safely stopped after starting.
- **Reversible** — the operation itself can be undone.
- **Compensatable** — a separate registered action can reverse or mitigate its effect.
- **Confirmation-required** — the operation is inherently irreversible or consequential and requires explicit confirmation.

## Core rule

**Unknown operations are not assumed safe.**

An operation must have an explicit profile before the system can reason about cancellation or compensation semantics.

## Example

```text
send_email
  cancelable: yes
  reversible: no
  compensatable: maybe

publish_public_content
  cancelable: no
  reversible: no
  compensatable: no
  confirmation_required: yes
```

The registry describes the operation. It does not execute it.

## Architecture

`Task → Side-Effect Profile → Authorization Receipt → Execution → Side-Effect State → Cancellation / Compensation`

## Why this matters

The Personal Intelligence will eventually interact with real systems: email, files, GitHub, calendars, financial services, and other tools. Those actions do not all have the same consequences.

The intelligence should know the consequence model **before** acting, rather than discovering afterward that an action could not be undone.

## Security

The registry contains operation metadata only. It contains no credentials, API keys, private payloads, or provider secrets.

## Next step

PI-045 should add **Explicit Confirmation Gates** for consequential operations, connecting the side-effect profile to a human approval boundary before execution.
