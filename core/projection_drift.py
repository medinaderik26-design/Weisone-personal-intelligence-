"""PI-080 lifecycle projection comparison."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectionDrift:
    changed: bool
    changes: tuple[str, ...] = ()


class ProjectionDriftDetector:
    """Describe projection changes without deciding whether they are errors."""

    def compare(self, previous, current) -> ProjectionDrift:
        if previous.task_id != current.task_id:
            raise ValueError("projection task IDs do not match")

        changes = []
        if previous.intent_id != current.intent_id:
            changes.append("intent_id")
        if previous.stages != current.stages:
            changes.append("stages")
        if previous.current_stage != current.current_stage:
            changes.append("current_stage")
        if previous.evidence_complete != current.evidence_complete:
            changes.append("evidence_complete")

        return ProjectionDrift(bool(changes), tuple(changes))
