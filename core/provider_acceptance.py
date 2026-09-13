"""PI-089 execution-start -> provider-acceptance boundary."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class ProviderAcceptanceResult:
    task_id: str
    dispatch_key: str
    intent_id: str
    provider: str
    accepted: bool
    recorded_at: str
    reason: str

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.dispatch_key:
            raise ValueError("dispatch_key is required")
        if not self.intent_id:
            raise ValueError("intent_id is required")
        if not self.provider:
            raise ValueError("provider is required")
        if not self.recorded_at:
            raise ValueError("recorded_at is required")


class ProviderAcceptanceBoundary:
    """Record provider acceptance without claiming external completion."""

    def accept(self, execution_start, *, provider: str, accepted: bool, now=None) -> ProviderAcceptanceResult:
        if not execution_start.task_id:
            raise ValueError("task_id is required")
        if not execution_start.dispatch_key:
            raise ValueError("dispatch_key is required")
        if not execution_start.intent_id:
            raise ValueError("intent_id is required")
        if not provider:
            raise ValueError("provider is required")

        timestamp = now or datetime.now(timezone.utc)
        if not execution_start.started:
            result = ProviderAcceptanceResult(
                execution_start.task_id,
                execution_start.dispatch_key,
                execution_start.intent_id,
                provider,
                False,
                timestamp.isoformat(),
                "provider acceptance is blocked because execution has not started",
            )
            result.validate()
            return result

        result = ProviderAcceptanceResult(
            execution_start.task_id,
            execution_start.dispatch_key,
            execution_start.intent_id,
            provider,
            accepted,
            timestamp.isoformat(),
            "provider accepted the execution request"
            if accepted
            else "provider did not accept the execution request",
        )
        result.validate()
        return result
