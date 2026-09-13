"""PI-059 recovery and reconciliation for durable action history."""

from dataclasses import dataclass
from typing import Optional

from .durable_action_ledger import SQLiteActionLedger
from .persistent_work_state import WorkState


@dataclass(frozen=True)
class LedgerRecoveryDecision:
    task_id: str
    action: str
    reason: str
    current_stage: Optional[str] = None
    intent_id: Optional[str] = None


class ActionLedgerRecovery:
    """Inspect durable ledger state without assuming external completion."""

    def __init__(self, ledger: SQLiteActionLedger) -> None:
        self.ledger = ledger

    def inspect(self, state: WorkState) -> LedgerRecoveryDecision:
        state.validate()
        entries = self.ledger.for_task(state.task_id)

        if not entries:
            if state.status == "queued":
                return LedgerRecoveryDecision(
                    state.task_id, "resume", "no action history exists and work remains queued"
                )
            return LedgerRecoveryDecision(
                state.task_id, "human_review", "work state exists without corresponding action history"
            )

        latest = entries[-1]

        if latest.stage == "externally_confirmed":
            return LedgerRecoveryDecision(
                state.task_id,
                "complete",
                "durable ledger contains externally confirmed completion",
                latest.stage,
                latest.intent_id,
            )

        if latest.stage in {"cancelled", "human_review"}:
            return LedgerRecoveryDecision(
                state.task_id,
                "human_review",
                "latest ledger state requires human disposition",
                latest.stage,
                latest.intent_id,
            )

        if latest.stage in {"provider_accepted", "executing"}:
            return LedgerRecoveryDecision(
                state.task_id,
                "verify_external_effect",
                "execution may have produced an external effect; completion must be verified before retry",
                latest.stage,
                latest.intent_id,
            )

        if latest.stage == "failed":
            return LedgerRecoveryDecision(
                state.task_id,
                "retry_or_reroute",
                "prior attempt failed; existing retry and routing policies must decide the next execution",
                latest.stage,
                latest.intent_id,
            )

        if latest.stage in {"planned", "confirmed", "authorized", "retrying", "rerouted", "deferred"}:
            return LedgerRecoveryDecision(
                state.task_id,
                "resume_or_defer",
                "action is incomplete and has no evidence of external completion",
                latest.stage,
                latest.intent_id,
            )

        return LedgerRecoveryDecision(
            state.task_id,
            "human_review",
            "unrecognized ledger state requires review",
            latest.stage,
            latest.intent_id,
        )
