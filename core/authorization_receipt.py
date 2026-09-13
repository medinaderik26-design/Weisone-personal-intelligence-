"""PI-042 authorization receipts binding decisions to current epochs."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .authorization_epoch import AuthorizationEpoch, AuthorizationEpochGuard
from .revocation import RevocationGuard


@dataclass(frozen=True)
class AuthorizationReceipt:
    task_id: str
    subject: str
    provider: str
    task_type: str
    epoch: AuthorizationEpoch
    allowed: bool
    reason: str
    issued_at: datetime


@dataclass(frozen=True)
class ReceiptCheck:
    allowed: bool
    reason: str


class AuthorizationReceiptIssuer:
    def issue(
        self,
        *,
        task_id: str,
        subject: str,
        epoch: AuthorizationEpoch,
        allowed: bool,
        reason: str,
        now: Optional[datetime] = None,
    ) -> AuthorizationReceipt:
        if not task_id or not subject or not reason:
            raise ValueError("task_id, subject, and reason are required")
        return AuthorizationReceipt(
            task_id=task_id,
            subject=subject,
            provider=epoch.provider,
            task_type=epoch.task_type,
            epoch=epoch,
            allowed=allowed,
            reason=reason,
            issued_at=now or datetime.now(timezone.utc),
        )


class AuthorizationReceiptGuard:
    """Final freshness/revocation check before an execution boundary."""

    def __init__(self, epoch_guard: AuthorizationEpochGuard, revocation_guard: RevocationGuard) -> None:
        self.epoch_guard = epoch_guard
        self.revocation_guard = revocation_guard

    def check(self, receipt: AuthorizationReceipt) -> ReceiptCheck:
        if not receipt.allowed:
            return ReceiptCheck(False, "authorization receipt denies execution")

        epoch = self.epoch_guard.check(receipt.epoch)
        if not epoch.current:
            return ReceiptCheck(False, epoch.reason)

        revoked = self.revocation_guard.check(
            receipt.subject,
            receipt.provider,
            receipt.task_type,
        )
        if not revoked.allowed:
            return ReceiptCheck(False, revoked.reason)

        return ReceiptCheck(True, "authorization receipt is current and not revoked")
