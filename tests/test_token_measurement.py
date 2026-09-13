import pytest

from core.token_measurement import TokenMeasurement, TokenMeasurementAdapter


def fake_tokenizer(text: str) -> int:
    return len(text.split())


def test_tokenizer_adapter_records_source():
    measurement = TokenMeasurementAdapter(fake_tokenizer, "local", "test-model").measure_input("one two three")
    assert measurement.input_tokens == 3
    assert measurement.source == "tokenizer"


def test_unknown_measurements_are_allowed():
    measurement = TokenMeasurement("cloud", "model")
    measurement.validate()
    assert measurement.input_tokens is None


def test_negative_counts_rejected():
    with pytest.raises(ValueError):
        TokenMeasurement("cloud", "model", input_tokens=-1).validate()


def test_invalid_source_rejected():
    with pytest.raises(ValueError):
        TokenMeasurement("cloud", "model", source="characters").validate()
