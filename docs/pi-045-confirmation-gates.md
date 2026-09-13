# PI-045 — Explicit Confirmation Gates

## Purpose

Create a human approval boundary for consequential operations before the Personal Intelligence can execute them.

## Core rule

**If an operation is marked confirmation-required, no confirmation means no execution.**

The gate does not execute the operation. It only determines whether the authorization boundary has been satisfied.

## Flow

`Task → Side-Effect Profile → Confirmation Request → Human Decision → Authorization Receipt → Execution`

## Outcomes

- **Confirmed** → operation may continue through the remaining authorization and execution controls.
- **Denied / not confirmed** → operation is blocked.
- **Not required** → operation may continue if all other controls pass.

## Why this matters

The Personal Intelligence should automate routine work without silently taking consequential actions on the person's behalf.

Examples that may eventually require explicit confirmation include:
- publishing public content
- sending high-consequence messages
- financial transactions
- deleting important data
- irreversible account or system changes

The actual classification belongs in the side-effect registry and should be conservative.

## Safety

Confirmation is not a substitute for consent, provider policy, data boundaries, permissions, quota, or resource checks. It is an additional human-control layer.

## Next step

PI-046 should define **Action Scope & Transaction Boundaries**, so one confirmation cannot accidentally authorize more work than the user intended.
