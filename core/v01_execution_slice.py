"""Personal Intelligence v0.1 executable slice.

One work item through gate -> receipt -> ledger -> propose -> run -> verify
-> continuity. This is an integration slice, not a new PI-09x boundary.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Protocol


@dataclass(frozen=True)
class ContinuityRecord:
    version: int
    identity_id: str
    open_work_ids: List[str] = field(default_factory=list)
    grants: List[str] = field(default_factory=list)
    revocations: List[str] = field(default_factory=list)
    last_receipt_ids: List[str] = field(default_factory=list)
    last_evidence_ids: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class GateDecision:
    work_id: str
    identity_id: str
    allowed: bool
    reason: str


@dataclass(frozen=True)
class AuthorizationReceipt:
    receipt_id: str
    work_id: str
    identity_id: str
    allowed: bool
    reason: str


@dataclass(frozen=True)
class Proposal:
    work_id: str
    status: str  # accepted | rejected | needs_confirm
    reason: str


@dataclass(frozen=True)
class RunResult:
    work_id: str
    success: bool
    output: str
    reason: str


@dataclass(frozen=True)
class VerificationEvidence:
    evidence_id: str
    work_id: str
    verified: bool
    reason: str


@dataclass(frozen=True)
class SliceResult:
    work_id: str
    receipt: AuthorizationReceipt
    proposal: Proposal
    run: RunResult | None
    evidence: VerificationEvidence | None
    continuity: ContinuityRecord


class Ledger:
    """Small append-only ledger for the v0.1 integration slice."""

    def __init__(self) -> None:
        self.entries: List[Dict[str, str]] = []

    def record(self, *, work_id: str, stage: str, value: str) -> None:
        self.entries.append(
            {
                "work_id": work_id,
                "stage": stage,
                "value": value,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            }
        )


class Provider(Protocol):
    def propose(self, work_id: str, operation: str) -> Proposal: ...
    def run(self, work_id: str, operation: str) -> RunResult: ...
    def verify(self, work_id: str, run: RunResult) -> VerificationEvidence: ...
    def cancel(self, work_id: str) -> None: ...
    def health(self) -> bool: ...


class StubProvider:
    """Deterministic provider used to exercise the full slice and failures."""

    def __init__(self, failure: str | None = None) -> None:
        self.failure = failure
        self.run_count = 0
        self.cancelled = False

    def propose(self, work_id: str, operation: str) -> Proposal:
        if self.failure == "provider_disappears":
            return Proposal(work_id, "rejected", "provider unavailable")
        if self.failure == "reject":
            return Proposal(work_id, "rejected", "stub rejected proposal")
        if self.failure == "needs_confirm":
            return Proposal(work_id, "needs_confirm", "explicit confirmation required")
        return Proposal(work_id, "accepted", "stub accepted proposal")

    def run(self, work_id: str, operation: str) -> RunResult:
        self.run_count += 1
        if self.failure == "duplicate_run" and self.run_count > 1:
            return RunResult(work_id, False, "", "duplicate execution blocked")
        if self.failure == "run_failure":
            return RunResult(work_id, False, "", "stub execution failed")
        return RunResult(work_id, True, f"stub:{operation}", "stub execution completed")

    def verify(self, work_id: str, run: RunResult) -> VerificationEvidence:
        if self.failure == "verify_failure":
            return VerificationEvidence("evidence-failed", work_id, False, "verification failed")
        return VerificationEvidence("evidence-ok", work_id, run.success, "verified against work_id")

    def cancel(self, work_id: str) -> None:
        self.cancelled = True

    def health(self) -> bool:
        return self.failure != "provider_disappears"


class PersonalIntelligenceSlice:
    """Execute one work_id without adding another PI-09x boundary."""

    def __init__(self, provider: Provider, *, identity_id: str = "person-001") -> None:
        self.provider = provider
        self.identity_id = identity_id
        self.ledger = Ledger()
        self._receipt_counter = 0
        self.continuity = ContinuityRecord(version=1, identity_id=identity_id)

    def execute(
        self,
        work_id: str,
        operation: str,
        *,
        authorized: bool = True,
    ) -> SliceResult:
        if not work_id:
            raise ValueError("work_id is required")
        if not operation:
            raise ValueError("operation is required")

        gate = GateDecision(
            work_id=work_id,
            identity_id=self.identity_id,
            allowed=authorized,
            reason="authorized" if authorized else "authorization denied",
        )
        self._add_open_work(work_id)
        self.ledger.record(work_id=work_id, stage="gate", value=gate.reason)

        self._receipt_counter += 1
        receipt = AuthorizationReceipt(
            receipt_id=f"receipt-{self._receipt_counter}",
            work_id=work_id,
            identity_id=self.identity_id,
            allowed=gate.allowed,
            reason=gate.reason,
        )
        self.ledger.record(work_id=work_id, stage="receipt", value=receipt.receipt_id)

        if not receipt.allowed:
            proposal = Proposal(work_id, "rejected", "execution blocked by authorization receipt")
            self.ledger.record(work_id=work_id, stage="proposal", value=proposal.status)
            return SliceResult(work_id, receipt, proposal, None, None, self.continuity)

        proposal = self.provider.propose(work_id, operation)
        self.ledger.record(work_id=work_id, stage="proposal", value=proposal.status)

        if proposal.status != "accepted":
            # needs_confirm is a real gate stop. No timeout path runs the work.
            return SliceResult(work_id, receipt, proposal, None, None, self.continuity)

        run = self.provider.run(work_id, operation)
        self.ledger.record(work_id=work_id, stage="run", value="success" if run.success else "failed")
        if not run.success:
            return SliceResult(work_id, receipt, proposal, run, None, self.continuity)

        evidence = self.provider.verify(work_id, run)
        self.ledger.record(work_id=work_id, stage="verify", value=evidence.evidence_id)
        if not evidence.verified or evidence.work_id != work_id:
            return SliceResult(work_id, receipt, proposal, run, evidence, self.continuity)

        self._complete_work(work_id, receipt.receipt_id, evidence.evidence_id)
        return SliceResult(work_id, receipt, proposal, run, evidence, self.continuity)

    def _add_open_work(self, work_id: str) -> None:
        if work_id not in self.continuity.open_work_ids:
            self.continuity = ContinuityRecord(
                version=self.continuity.version,
                identity_id=self.continuity.identity_id,
                open_work_ids=[*self.continuity.open_work_ids, work_id],
                grants=self.continuity.grants,
                revocations=self.continuity.revocations,
                last_receipt_ids=self.continuity.last_receipt_ids,
                last_evidence_ids=self.continuity.last_evidence_ids,
            )

    def _complete_work(self, work_id: str, receipt_id: str, evidence_id: str) -> None:
        self.continuity = ContinuityRecord(
            version=self.continuity.version,
            identity_id=self.continuity.identity_id,
            open_work_ids=[x for x in self.continuity.open_work_ids if x != work_id],
            grants=self.continuity.grants,
            revocations=self.continuity.revocations,
            last_receipt_ids=[*self.continuity.last_receipt_ids, receipt_id],
            last_evidence_ids=[*self.continuity.last_evidence_ids, evidence_id],
        )
