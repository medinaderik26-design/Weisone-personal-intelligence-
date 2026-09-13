"""PI-078 durable end-to-end lifecycle projection."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LifecycleProjection:
    task_id: str
    intent_id: Optional[str]
    stages: tuple[str, ...]
    current_stage: Optional[str]
    evidence_complete: bool


class LifecycleProjector:
    """Reconstruct the known action lifecycle without inferring missing evidence."""

    def project(self, task_id: str, ledger_entries: tuple, *, receipts: tuple = ()) -> LifecycleProjection:
        if not task_id:
            raise ValueError("task_id is required")

        entries = [entry for entry in ledger_entries if entry.task_id == task_id]
        if not entries:
            return LifecycleProjection(task_id, None, (), None, False)

        intent_ids = {entry.intent_id for entry in entries if entry.intent_id}
        if len(intent_ids) > 1:
            raise ValueError("multiple execution intents found for one task")

        stages = tuple(entry.stage for entry in entries)
        intent_id = next(iter(intent_ids), None)
        current = stages[-1] if stages else None

        required_terminal = "externally_confirmed"
        evidence_complete = current == required_terminal

        return LifecycleProjection(
            task_id=task_id,
            intent_id=intent_id,
            stages=stages,
            current_stage=current,
            evidence_complete=evidence_complete,
        )
