from core.retry_policy import RetryPolicy


def test_success_never_retries():
    decision = RetryPolicy().decide(attempt=1, success=True, retryable=True)
    assert decision.retry is False


def test_non_retryable_failure_stops():
    decision = RetryPolicy().decide(attempt=1, success=False, retryable=False)
    assert decision.retry is False


def test_retry_uses_exponential_backoff():
    policy = RetryPolicy(max_attempts=3, base_delay_seconds=2.0)
    first = policy.decide(attempt=1, success=False, retryable=True)
    second = policy.decide(attempt=2, success=False, retryable=True)

    assert first.retry and first.delay_seconds == 2.0
    assert second.retry and second.delay_seconds == 4.0


def test_max_attempts_stops_retry():
    decision = RetryPolicy(max_attempts=3).decide(
        attempt=3, success=False, retryable=True
    )
    assert decision.retry is False
