"""PI-048 execution intent IDs binding approval to one execution scope."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from .action_plan import ActionPlan, PlanConfirmation


@dataclass(frozen=True)
class ExecutionIntent:
    intent_id: str
    task_id: str
    scope_id: str
    confirmed_effects: tuple[str, ...]
    issued_at: datetime
    consumed: bool = False


class ExecutionIntentRegistry:
    """One-shot execution intents for safely controlled external actions."""

    def __init__(self) -> None:
        self._intents: dict[str, ExecutionIntent] = {}

    def issue(self, confirmation: PlanConfirmation, *, now: Optional[datetime] = None) -> ExecutionIntent:
        intent = ExecutionIntent(
            intent_id=str(uuid4()),
            task_id=confirmation.task_id,
            scope_id=confirmation.scope_id,
            confirmed_effects=confirmation.confirmed_effects,
            issued_at=now or datetime.now(timezone.utc),
        )
        self._intents[intent.intent_id] = intent
        return intent

    def consume(self, intent_id: str) -> ExecutionIntent:
        intent = self._intents.get(intent_id)
        if intent is None:
            raise KeyError("unknown execution intent")
        if intent.consumed:
            raise RuntimeError("execution intent has already been consumed")
        consumed = ExecutionIntent(
            intent_id=intent.intent_id,
            task_id=intent.task_id,
            scope_id=intent.scope_id,
            confirmed_effects=intent.confirmed_effects,
            issued_at=intent.issued_at,
            consumed=True,
        )
        self._intents[intent_id] = consumed
        return consumed

    def get(self, intent_id: str) -> Optional[ExecutionIntent]:
        return self._intents.get(intent_id)


def issue_from_plan(plan: ActionPlan, confirmation: PlanConfirmation, registry: ExecutionIntentRegistry) -> ExecutionIntent:
    plan.validate()
    if confirmation.task_id != plan.scope.task_id:
        raise ValueError("confirmation task does not match action plan")
    if tuple(effect.effect for effect in plan.effects) != confirmation.confirmed_effects:
        raise ValueError("confirmed effects do not match action plan")
    return registry.issue(confirmation)
