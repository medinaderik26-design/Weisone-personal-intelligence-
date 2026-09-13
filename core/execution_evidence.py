"""PI-014 unified execution evidence."""

from dataclasses import dataclass
from typing import Optional

from .execution_telemetry import ExecutionTelemetry
from .resource_outcome import ResourceOutcome


@dataclass(frozen=True)
class ExecutionEvidence:
    """One provider-neutral evidence record for a completed execution."""

    telemetry: ExecutionTelemetry
    resource: ResourceOutcome

    def validate(self) -> None:
        self.telemetry.validate()
        self.resource.validate()

        if self.telemetry.task_id != self.resource.task_id:
            raise ValueError("telemetry and resource task IDs must match")
        if self.telemetry.provider != self.resource.provider:
            raise ValueError("telemetry and resource providers must match")


class ExecutionEvidenceRecorder:
    """Validate and retain unified execution evidence."""

    def __init__(self) -> None:
        self.records: list[ExecutionEvidence] = []

    def record(self, evidence: ExecutionEvidence) -> ExecutionEvidence:
        evidence.validate()
        self.records.append(evidence)
        return evidence

    def latest(self) -> Optional[ExecutionEvidence]:
        return self.records[-1] if self.records else None

    def for_task(self, task_id: str) -> list[ExecutionEvidence]:
        return [record for record in self.records if record.telemetry.task_id == task_id]
