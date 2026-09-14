"""Ollama provider for the Personal Intelligence v0.1 execution slice.

The provider implements the same contract as StubProvider. It does not change
slice semantics; it only replaces the model execution mechanism.
"""

from dataclasses import dataclass
import json
from typing import Callable
from urllib.error import URLError
from urllib.request import Request, urlopen

from .v01_execution_slice import Proposal, RunResult, VerificationEvidence


@dataclass(frozen=True)
class OllamaResponse:
    status: int
    body: dict


class OllamaProvider:
    """Minimal Ollama adapter using Ollama's local HTTP API."""

    def __init__(
        self,
        model: str,
        *,
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: float = 30.0,
        request: Callable[[str, bytes], OllamaResponse] | None = None,
    ) -> None:
        if not model:
            raise ValueError("model is required")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._request = request or self._http_request

    def propose(self, work_id: str, operation: str) -> Proposal:
        if not self.health():
            return Proposal(work_id, "rejected", "ollama unavailable")
        return Proposal(work_id, "accepted", "ollama provider ready")

    def run(self, work_id: str, operation: str) -> RunResult:
        payload = {
            "model": self.model,
            "prompt": operation,
            "stream": False,
        }
        try:
            response = self._request(
                f"{self.base_url}/api/generate",
                json.dumps(payload).encode("utf-8"),
            )
        except (OSError, URLError) as exc:
            return RunResult(work_id, False, "", f"ollama request failed: {exc}")

        if response.status != 200:
            return RunResult(work_id, False, "", f"ollama returned HTTP {response.status}")

        output = response.body.get("response")
        if not isinstance(output, str):
            return RunResult(work_id, False, "", "ollama response missing text")

        return RunResult(work_id, True, output, "ollama execution completed")

    def verify(self, work_id: str, run: RunResult) -> VerificationEvidence:
        if not run.success:
            return VerificationEvidence(
                "ollama-verification-failed",
                work_id,
                False,
                "run did not succeed",
            )
        return VerificationEvidence(
            "ollama-evidence-ok",
            work_id,
            True,
            "verified against work_id",
        )

    def cancel(self, work_id: str) -> None:
        # v0.1 has no remote cancellation contract. Keeping this explicit
        # avoids pretending that an HTTP request can cancel an in-flight model.
        return None

    def health(self) -> bool:
        try:
            response = self._request(f"{self.base_url}/api/tags", b"")
        except (OSError, URLError):
            return False
        return response.status == 200

    def _http_request(self, url: str, body: bytes) -> OllamaResponse:
        method = "POST" if body else "GET"
        request = Request(
            url,
            data=body or None,
            method=method,
            headers={"Content-Type": "application/json"} if body else {},
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:
            raw = response.read().decode("utf-8")
            return OllamaResponse(response.status, json.loads(raw) if raw else {})
