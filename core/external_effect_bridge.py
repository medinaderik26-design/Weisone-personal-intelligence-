"""PI-091 provider acceptance -> external-effect verification boundary."""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class ExternalVerificationRequest:
    task_id: str
    dispatch_key: str
    intent_id: str
    provider: str
    operation: str
    target: str
    eligible: bool
    reason: str


class ExternalEffectVerificationBridge:
    """Create verification requests without claiming external completion."""

    def build(
        self,
        provider_result: Any,
        *,
        operation: str,
        target: str,
    ) -> ExternalVerificationRequest:
        required = {
            "task_id": provider_result.task_id,
            "dispatch_key": provider_result.dispatch_key,
            "intent_id": provider_result.intent_id,
            "provider": provider_result.provider,
            "operation": operation,
            "target": target,
        }
        for name, value in required.items():
            if not value:
                raise ValueError(f"{name} is required")

        if not provider_result.accepted:
            return ExternalVerificationRequest(
                **required,
                eligible=False,
                reason="external verification is blocked because provider acceptance was not confirmed",
            )

        return ExternalVerificationRequest(
            **required,
            eligible=True,
            reason="provider acceptance permits an external-effect verification attempt",
        )
