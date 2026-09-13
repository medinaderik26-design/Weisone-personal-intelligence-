"""PI-050 traceability from confirmed intent to measured execution evidence."""

from dataclasses import dataclass
from typing import Optional

from .execution_evidence import ExecutionEvidence
from .execution_intent import ExecutionIntent
from .idempotency import ExecutionReceipt


@dataclass(frozen=True)
class IntentExecutionEvidence:
    """Bind one confirmed intent to one measured execution outcome."""

    intent: ExecutionIntent
    evidence: ExecutionEvidence
    receipt: ExecutionReceipt

    def validate(self) -> None:
        self.evidence.validate()

        if self.intent.task_id != self.evidence.telemetry.task_id:
            raise ValueError("intent and telemetry task IDs must match")
        if self.intent.task_id != self.evidence.resource.task_id:
            raise ValueError("intent and resource task IDs must match")
        if self.intent.task_id != self.receipt.task_id:
            raise ValueError("intent and receipt task IDs must match")
        if self.intent.intent_id != self.receipt.execution_key:
            raise ValueError("intent ID and execution key must match")
        if self.intent.provider if hasattr(self.intent, "provider") else False:
            raise ValueError("unexpected provider field")


class IntentEvidenceRecorder:
    """Validate and retain intent-to-outcome trace records."""

    def __init__(self) -> None:
        self.records: list[IntentExecutionEvidence] = []

    def record(self, trace: IntentExecutionEvidence) -> IntentExecutionEvidence:
        trace.validate()
        self.records.append(trace)
        return trace

    def for_intent(self, intent_id: str) -> list[IntentExecutionEvidence]:
        return [record for record in self.records if record.intent.intent_id == intent_id]

    def for_task(self, task_id: str) -> list[IntentExecutionEvidence]:
        return [record for record in self.records if record.intent.task_id == task_id]
