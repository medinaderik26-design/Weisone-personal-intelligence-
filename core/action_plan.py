"""PI-047 concrete action plans and confirmation previews."""

from dataclasses import dataclass
from typing import Tuple

from .action_scope import ActionScope


@dataclass(frozen=True)
class PlannedEffect:
    effect: str
    target: str
    description: str
    reversible: bool = False
    compensation: str = ""


@dataclass(frozen=True)
class ActionPlan:
    scope: ActionScope
    effects: Tuple[PlannedEffect, ...]

    def validate(self) -> None:
        self.scope.validate()
        for effect in self.effects:
            if not effect.effect or not effect.target or not effect.description:
                raise ValueError("planned effects require effect, target, and description")
            if effect.effect not in self.scope.allowed_effects:
                raise ValueError("planned effect is outside the action scope")

    def preview(self) -> tuple[str, ...]:
        self.validate()
        return tuple(
            f"{effect.effect} → {effect.target}: {effect.description}"
            for effect in self.effects
        )


@dataclass(frozen=True)
class PlanConfirmation:
    task_id: str
    scope_id: str
    confirmed_effects: Tuple[str, ...]


class ActionPlanGuard:
    def confirm(self, plan: ActionPlan, *, confirmed: bool) -> PlanConfirmation:
        plan.validate()
        if not confirmed:
            raise PermissionError("explicit confirmation required for action plan")
        scope_id = plan.scope.scope_id or plan.scope.task_id
        return PlanConfirmation(
            task_id=plan.scope.task_id,
            scope_id=scope_id,
            confirmed_effects=tuple(effect.effect for effect in plan.effects),
        )
