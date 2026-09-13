import pytest

from core.tokenizer_adapters import GenericTokenizerAdapter, TiktokenAdapter, provider_reported_measurement


class FakeTokenizer:
    def count(self, text: str) -> int:
        return len(text.split())


def test_generic_adapter_uses_exact_adapter_count():
    measurement = GenericTokenizerAdapter(FakeTokenizer(), "local", "fake-model").measure("one two three")
    assert measurement.input_tokens == 3
    assert measurement.source == "tokenizer"


def test_provider_reported_measurement_preserves_unknowns():
    measurement = provider_reported_measurement(
        provider="cloud",
        model="model",
        input_tokens=12,
        output_tokens=None,
    )
    assert measurement.input_tokens == 12
    assert measurement.output_tokens is None
    assert measurement.source == "provider_reported"


def test_provider_reported_negative_count_rejected():
    with pytest.raises(ValueError):
        provider_reported_measurement(provider="cloud", model="model", input_tokens=-1)


def test_tiktoken_adapter_is_explicit_when_dependency_missing():
    try:
        import tiktoken  # noqa: F401
    except ImportError:
        with pytest.raises(RuntimeError, match="tiktoken is required"):
            TiktokenAdapter("test-model")
