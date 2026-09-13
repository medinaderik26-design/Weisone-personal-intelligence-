"""PI-084 bridge policy boundary decisions to scheduler dispatch requests."""

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class PolicyDispatchRequest:
    task_id: str
    classification: str
    action: str
    dispatch_key: str | None
    eligible: bool
    reason: str


class PolicyDispatchBridge:
    """Translate an execution-boundary decision into a scheduler dispatch request.

    This bridge does not authorize, execute, or durably claim work. The durable
    claim remains the responsibility of SQLiteRecoveryDispatchStore.
    """

    @staticmethod
    def make_dispatch_key(task_id: str, classification: str, action: str) -> str:
        if not task_id or not classification or not action:
            raise ValueError("task_id, classification, and action are required")
        raw = f"{task_id}|{classification}|{action}".encode("utf-8")
        return sha256(raw).hexdigest()

    def build(self, boundary_decision, classification: str) -> PolicyDispatchRequest:
        if not boundary_decision.task_id:
            raise ValueError("task_id is required")
        if not boundary_decision.action:
            raise ValueError("action is required")
        if not classification:
            raise ValueError("classification is required")

        if not boundary_decision.handoff_allowed:
            return PolicyDispatchRequest(
                task_id=boundary_decision.task_id,
                classification=classification,
                action=boundary_decision.action,
                dispatch_key=None,
                eligible=False,
                reason=boundary_decision.reason,
            )

        if boundary_decision.action != "continue":
            return PolicyDispatchRequest(
                task_id=boundary_decision.task_id,
                classification=classification,
                action=boundary_decision.action,
                dispatch_key=None,
                eligible=False,
                reason="only the explicit continue decision may cross the dispatch boundary",
            )

        key = self.make_dispatch_key(
            boundary_decision.task_id,
            classification,
            boundary_decision.action,
        )
        return PolicyDispatchRequest(
            task_id=boundary_decision.task_id,
            classification=classification,
            action=boundary_decision.action,
            dispatch_key=key,
            eligible=True,
            reason="policy boundary permits scheduler dispatch claim",
        )
