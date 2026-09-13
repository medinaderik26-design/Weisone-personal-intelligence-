from core.authorization_audit import AuthorizationAuditEvent, AuthorizationAuditLog


def test_audit_records_allowed_decision():
    log = AuthorizationAuditLog()
    event = AuthorizationAuditEvent("t1", "local", True, "authorized")
    log.record(event)
    assert log.latest("t1") == event


def test_audit_records_denial_reason():
    log = AuthorizationAuditLog()
    log.record(AuthorizationAuditEvent("t2", "cloud", False, "high privacy is local-only"))
    events = log.for_task("t2")
    assert len(events) == 1
    assert events[0].allowed is False
    assert events[0].reason == "high privacy is local-only"


def test_audit_is_append_only_from_public_api():
    log = AuthorizationAuditLog()
    first = AuthorizationAuditEvent("t3", "local", True, "authorized")
    second = AuthorizationAuditEvent("t3", "cloud", False, "provider denied")
    log.record(first)
    log.record(second)
    events = log.all()
    events.clear()
    assert len(log.all()) == 2


def test_invalid_event_rejected():
    log = AuthorizationAuditLog()
    try:
        log.record(AuthorizationAuditEvent("", "local", False, "denied"))
        assert False
    except ValueError:
        assert True
