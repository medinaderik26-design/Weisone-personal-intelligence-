from datetime import datetime, timezone

from core.execution_evidence import ExecutionEvidence
from core.execution_intent import ExecutionIntent
from core.execution_telemetry import ExecutionTelemetry
from core.idempotency import ExecutionReceipt
from core.intent_evidence import IntentExecutionEvidence, IntentEvidenceRecorder
from core.resource_outcome import ResourceOutcome


def make_trace():
    now = datetime.now(timezone.utc)
    intent = ExecutionIntent(
        intent_id="intent-1",
        task_id="task-1",
        scope_id="scope-1",
        confirmed_effects=("send",),
        issued_at=now,
    )
    telemetry = ExecutionTelemetry(
        task_id="task-1",
        task_type="communication",
        provider="local",
        model="test-model",
        success=True,
        latency_ms=12.0,
        input_tokens=10,
        output_tokens=5,
    )
    resource = ResourceOutcome(
        provider="local",
        task_id="task-1",
        input_tokens=10,
        output_tokens=5,
        latency_ms=12.0,
        cost=0.0,
    )
    evidence = ExecutionEvidence(telemetry=telemetry, resource=resource)
    receipt = ExecutionReceipt(
        execution_key="intent-1",
        task_id="task-1",
        success=True,
        response="completed",
    )
    return IntentExecutionEvidence(intent, evidence, receipt)


def test_intent_execution_evidence_binds_full_trace():
    trace = make_trace()
    trace.validate()
    assert trace.intent.intent_id == trace.receipt.execution_key
    assert trace.intent.task_id == trace.evidence.telemetry.task_id


def test_mismatched_intent_key_rejected():
    trace = make_trace()
    bad_receipt = ExecutionReceipt("other-intent", "task-1", True, "completed")
    bad = IntentExecutionEvidence(trace.intent, trace.evidence, bad_receipt)
    try:
        bad.validate()
        assert False
    except ValueError:
        pass


def test_mismatched_task_rejected():
    trace = make_trace()
    bad_receipt = ExecutionReceipt("intent-1", "task-2", True, "completed")
    bad = IntentExecutionEvidence(trace.intent, trace.evidence, bad_receipt)
    try:
        bad.validate()
        assert False
    except ValueError:
        pass


def test_recorder_indexes_by_intent_and_task():
    trace = make_trace()
    recorder = IntentEvidenceRecorder()
    recorder.record(trace)
    assert recorder.for_intent("intent-1") == [trace]
    assert recorder.for_task("task-1") == [trace]
