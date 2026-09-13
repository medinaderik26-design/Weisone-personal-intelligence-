"""PI-046 explicit action scopes and transaction boundaries."""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class ActionScope:
    task_id: str
    operation: str
    target: str
    purpose: str
    allowed_effects: Tuple[str, ...] = ()
    confirmation_required: bool = False
    scope_id: Optional[str] = None

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.operation:
            raise ValueError("operation is required")
        if not self.target:
            raise ValueError("target is required")
        if not self.purpose:
            raise ValueError("purpose is required")
        if any(not effect for effect in self.allowed_effects):
            raise ValueError("allowed_effects cannot contain empty values")

    def permits(self, effect: str) -> bool:
        self.validate()
        return effect in self.allowed_effects


@dataclass(frozen=True)
class ScopeCheck:
    allowed: bool
    reason: str


class ActionScopeGuard:
    def check(self, scope: ActionScope, *, operation: str, target: str, effect: str) -> ScopeCheck:
        scope.validate()
        if operation != scope.operation:
            return ScopeCheck(False, "operation is outside the authorized scope")
        if target != scope.target:
            return ScopeCheck(False, "target is outside the authorized scope")
        if not scope.permits(effect):
            return ScopeCheck(False, "requested effect is outside the authorized scope")
        return ScopeCheck(True, "action is within the authorized scope")
