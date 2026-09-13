"""PI-064 recovery snapshot comparison and drift detection."""

from dataclasses import dataclass
from typing import Optional

from .recovery_snapshot import RecoverySnapshot


@dataclass(frozen=True)
class RecoveryDrift:
    changed: bool
    changes: tuple[str, ...] = ()


class RecoveryDriftDetector:
    """Compare recovery snapshots without assuming which state is correct."""

    def compare(self, previous: RecoverySnapshot, current: RecoverySnapshot) -> RecoveryDrift:
        previous.validate()
        current.validate()

        if previous.task_id != current.task_id:
            raise ValueError("cannot compare snapshots for different tasks")

        changes = []
        if previous.work_state.status != current.work_state.status:
            changes.append("work_status")
        if previous.work_state.attempt_count != current.work_state.attempt_count:
            changes.append("attempt_count")
        if previous.work_state.provider != current.work_state.provider:
            changes.append("provider")
        if self._stage(previous) != self._stage(current):
            changes.append("ledger_stage")
        if self._action(previous) != self._action(current):
            changes.append("recovery_action")
        if self._reason(previous) != self._reason(current):
            changes.append("recovery_reason")
        if self._intent(previous) != self._intent(current):
            changes.append("intent_id")

        return RecoveryDrift(bool(changes), tuple(changes))

    @staticmethod
    def _stage(snapshot: RecoverySnapshot) -> Optional[str]:
        return None if snapshot.latest_ledger is None else snapshot.latest_ledger.stage

    @staticmethod
    def _action(snapshot: RecoverySnapshot) -> str:
        return snapshot.decision.action

    @staticmethod
    def _reason(snapshot: RecoverySnapshot) -> str:
        return snapshot.decision.reason

    @staticmethod
    def _intent(snapshot: RecoverySnapshot) -> Optional[str]:
        if snapshot.latest_ledger is not None:
            return snapshot.latest_ledger.intent_id
        return snapshot.decision.intent_id
