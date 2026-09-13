"""PI-051 external-effect receipts and completion evidence."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class ExternalEffectReceipt:
    intent_id: str
    task_id: str
    operation: str
    target: str
    status: str
    provider_reference: Optional[str] = None
    observed_at: Optional[datetime] = None
    evidence_source: str = "unknown"

    def validate(self) -> None:
        if not self.intent_id:
            raise ValueError("intent_id is required")
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.operation:
            raise ValueError("operation is required")
        if not self.target:
            raise ValueError("target is required")
        if self.status not in {"attempted", "accepted", "confirmed", "failed", "unknown"}:
            raise ValueError("invalid external effect status")
        if self.evidence_source not in {"provider_reported", "external_confirmed", "unknown"}:
            raise ValueError("invalid evidence source")


class ExternalEffectRegistry:
    """Retain explicit observations about external effects."""

    def __init__(self) -> None:
        self._receipts: dict[str, ExternalEffectReceipt] = {}

    def record(self, receipt: ExternalEffectReceipt) -> ExternalEffectReceipt:
        receipt.validate()
        existing = self._receipts.get(receipt.intent_id)
        if existing is not None and existing.task_id != receipt.task_id:
            raise ValueError("intent ID already belongs to another task")
        self._receipts[receipt.intent_id] = receipt
        return receipt

    def get(self, intent_id: str) -> Optional[ExternalEffectReceipt]:
        return self._receipts.get(intent_id)

    def confirmed(self, intent_id: str) -> bool:
        receipt = self.get(intent_id)
        return receipt is not None and receipt.status == "confirmed" and receipt.evidence_source == "external_confirmed"


def make_provider_acceptance(intent_id: str, task_id: str, operation: str, target: str, provider_reference: str) -> ExternalEffectReceipt:
    return ExternalEffectReceipt(
        intent_id=intent_id,
        task_id=task_id,
        operation=operation,
        target=target,
        status="accepted",
        provider_reference=provider_reference,
        observed_at=datetime.now(timezone.utc),
        evidence_source="provider_reported",
    )
