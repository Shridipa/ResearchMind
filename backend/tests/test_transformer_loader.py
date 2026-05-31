import pytest

from app.document_processing.transformer_summary import TransformerSummarizer


def test_summarizer_unavailable(monkeypatch):
    s = TransformerSummarizer(model_name="nonexistent/model")

    # Simulate failed load
    def _fake_load():
        s._loaded = True
        s.available = False
        s.last_error = "simulated failure"

    monkeypatch.setattr(s, "_load_model", _fake_load)

    # summarize should return None when model unavailable
    assert s.summarize("Some text") is None


def test_summarizer_successful(monkeypatch):
    s = TransformerSummarizer(model_name="mock/model")

    # Simulate a working pipeline
    def _fake_load():
        s._loaded = True
        s.available = True
        s._pipeline = lambda text, **kwargs: [{"summary_text": "ok"}]

    monkeypatch.setattr(s, "_load_model", _fake_load)

    out = s.summarize("This is a test.")
    assert out == "ok"


def test_summarizer_generation_exception(monkeypatch):
    s = TransformerSummarizer(model_name="mock/model")

    def _fake_load():
        s._loaded = True
        s.available = True

        def raise_pipeline(text, **kwargs):
            raise RuntimeError("generation error")

        s._pipeline = raise_pipeline

    monkeypatch.setattr(s, "_load_model", _fake_load)

    assert s.summarize("input") is None
    assert s.last_error and "generation error" in s.last_error or s.last_error
