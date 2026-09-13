from core.authorization_epoch import AuthorizationEpochGuard, AuthorizationEpochRegistry
from core.authorization_receipt import AuthorizationReceiptIssuer, AuthorizationReceiptGuard
from core.revocation import RevocationGuard, RevocationRegistry


def make_receipt(registry):
    epoch = registry.advance("person", "cloud", "summary")
    return AuthorizationReceiptIssuer().issue(
        task_id="t1",
        subject="person",
        epoch=epoch,
        allowed=True,
        reason="explicit authorization",
    )


def test_current_receipt_is_allowed():
    epochs = AuthorizationEpochRegistry()
    revocations = RevocationRegistry()
    receipt = make_receipt(epochs)
    result = AuthorizationReceiptGuard(
        AuthorizationEpochGuard(epochs), RevocationGuard(revocations)
    ).check(receipt)
    assert result.allowed is True


def test_stale_receipt_is_denied():
    epochs = AuthorizationEpochRegistry()
    revocations = RevocationRegistry()
    receipt = make_receipt(epochs)
    epochs.advance("person", "cloud", "summary")
    result = AuthorizationReceiptGuard(
        AuthorizationEpochGuard(epochs), RevocationGuard(revocations)
    ).check(receipt)
    assert result.allowed is False
    assert result.reason == "authorization decision is stale"


def test_revoked_receipt_is_denied():
    epochs = AuthorizationEpochRegistry()
    revocations = RevocationRegistry()
    receipt = make_receipt(epochs)
    revocations.revoke("person", "cloud", "summary")
    result = AuthorizationReceiptGuard(
        AuthorizationEpochGuard(epochs), RevocationGuard(revocations)
    ).check(receipt)
    assert result.allowed is False
    assert result.reason == "consent revoked"


def test_denied_receipt_cannot_execute():
    epochs = AuthorizationEpochRegistry()
    revocations = RevocationRegistry()
    epoch = epochs.advance("person", "cloud", "summary")
    receipt = AuthorizationReceiptIssuer().issue(
        task_id="t2",
        subject="person",
        epoch=epoch,
        allowed=False,
        reason="provider not authorized",
    )
    result = AuthorizationReceiptGuard(
        AuthorizationEpochGuard(epochs), RevocationGuard(revocations)
    ).check(receipt)
    assert result.allowed is False
