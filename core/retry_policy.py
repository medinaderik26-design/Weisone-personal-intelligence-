"""PI-019 retry decisions that preserve safety and idempotency."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryDecision:
    retry: bool
    reason: str
    delay_seconds: float = 0.0


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 1.0

    def decide(self, *, attempt: int, success: bool, retryable: bool) -> RetryDecision:
        if attempt < 1:
            raise ValueError("attempt must be at least 1")
        if success:
            return RetryDecision(False, "execution succeeded")
        if not retryable:
            return RetryDecision(False, "failure is not retryable")
        if attempt >= self.max_attempts:
            return RetryDecision(False, "maximum attempts reached")

        delay = self.base_delay_seconds * (2 ** (attempt - 1))
        return RetryDecision(True, "retryable failure", delay)
