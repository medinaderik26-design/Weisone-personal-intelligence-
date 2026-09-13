"""PI-073 recovery inspection for durable scheduler dispatch acknowledgements."""

from dataclasses import dataclass
from typing import Literal

from .durable_dispatch_ack import SQLiteDispatchAcknowledgementStore

RecoveryAction = Literal["resume_handoff", "verify_acceptance", "continue", "human_review"]


@dataclass(frozen=True)
class DispatchRecoveryDecision:
    task_id: str
    dispatch_key: str
    action: RecoveryAction
    reason: str


class RecoveryDispatchInspector:
    """Translate durable dispatch state into a safe recovery action.

    This class observes state only. It never executes, authorizes, or claims
    that an external action completed.
    """

    def __init__(self, store: SQLiteDispatchAcknowledgementStore) -> None:
        self.store = store

    def inspect(self, task_id: str, dispatch_key: str) -> DispatchRecoveryDecision:
        if not task_id:
            raise ValueError("task_id is required")
        if not dispatch_key:
            raise ValueError("dispatch_key is required")

        ack = self.store.get(dispatch_key)
        if ack is None:
            return DispatchRecoveryDecision(
                task_id, dispatch_key, "resume_handoff",
                "no durable scheduler acknowledgement exists",
            )
        if ack.task_id != task_id:
            raise ValueError("dispatch key is bound to a different task")
        if ack.state == "claimed":
            return DispatchRecoveryDecision(
                task_id, dispatch_key, "resume_handoff",
                "dispatch was claimed but handoff was not confirmed",
            )
        if ack.state == "handed_off":
            return DispatchRecoveryDecision(
                task_id, dispatch_key, "verify_acceptance",
                "dispatch was handed off but scheduler acceptance is not confirmed",
            )
        if ack.state == "accepted":
            return DispatchRecoveryDecision(
                task_id, dispatch_key, "continue",
                "scheduler acceptance is durably confirmed; execution outcome remains a separate boundary",
            )
        return DispatchRecoveryDecision(
            task_id, dispatch_key, "human_review",
            "unknown acknowledgement state requires review",
        )
