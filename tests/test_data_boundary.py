from core.data_boundary import DataBoundary, DataField
from core.models import Task


def test_normal_task_only_sends_authorized_purpose_fields():
    task = Task(task_id="t1", prompt="summarize", task_type="summary")
    fields = [
        DataField("document", "normal", "summary"),
        DataField("password", "secret", "summary"),
        DataField("calendar", "normal", "calendar"),
    ]
    result = DataBoundary().filter(
        task,
        fields,
        provider="cloud",
        authorized_sensitivities={"normal"},
    )
    assert result.allowed is True
    assert result.fields == ("document",)
    assert result.denied_fields == ("password", "calendar")


def test_high_privacy_is_local_only():
    task = Task(task_id="t2", prompt="private", privacy="high")
    fields = [DataField("private_note", "sensitive", "general")]
    result = DataBoundary().filter(
        task,
        fields,
        provider="cloud",
        authorized_sensitivities={"sensitive"},
    )
    assert result.allowed is False


def test_high_privacy_can_use_local():
    task = Task(task_id="t3", prompt="private", privacy="high")
    fields = [DataField("private_note", "sensitive", "general")]
    result = DataBoundary().filter(
        task,
        fields,
        provider="local",
        authorized_sensitivities={"sensitive"},
    )
    assert result.allowed is True
    assert result.fields == ("private_note",)
