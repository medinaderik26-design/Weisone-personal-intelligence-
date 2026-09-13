from core.authorization_record import AuthorizationDecisionLog, AuthorizationDecisionRecord


def test_decision_record_captures_reason_and_policy_sources():
    record = AuthorizationDecisionRecord.create(
        task_id="t1",
        subject="person",
        provider="local",
        task_type="summary",
        allowed=True,
        reason="explicit consent and provider policy allow execution",
        fields_allowed=("document",),
        fields_denied=("password",),
        policy_sources=("consent", "provider_policy", "data_boundary"),
    )
    assert record.allowed is True
    assert record.fields_allowed == ("document",)
    assert "consent" in record.policy_sources
    assert record.to_dict()["provider"] == "local"


def test_decision_log_is_append_only_from_public_api():
    log = AuthorizationDecisionLog()
    record = AuthorizationDecisionRecord.create(
        task_id="t2",
        subject="person",
        provider="cloud",
        task_type="general",
        allowed=False,
        reason="consent missing",
        policy_sources=("consent",),
    )
    log.append(record)
    assert log.all() == (record,)
    assert log.for_task("t2") == (record,)


def test_record_requires_reason_and_identity():
    try:
        AuthorizationDecisionRecord.create(
            task_id="",
            subject="person",
            provider="cloud",
            task_type="general",
            allowed=False,
            reason="blocked",
        )
        assert False
    except ValueError:
        pass
