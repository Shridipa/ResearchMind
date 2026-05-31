"""Transformer-based abstractive summarization using HuggingFace models."""

from typing import Optional

try:
    from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except Exception:
    TRANSFORMERS_AVAILABLE = False


class TransformerSummarizer:
    """Robust seq2seq summarizer using AutoModelForSeq2SeqLM + AutoTokenizer with lazy loading."""

    def __init__(
        self,
        model_name: str = "facebook/bart-large-cnn",
        max_length: int = 150,
        min_length: int = 50,
        device: int = -1,
    ):
        self.model_name = model_name
        self.max_length = max_length
        self.min_length = min_length
        self.device = device
        self._tokenizer = None
        self._model = None
        self._pipeline = None
        self._loaded = False
        self.available = False
        self.last_error: str | None = None

    def _try_pipeline(self, task_name: str) -> Optional[object]:
        try:
            return pipeline(task_name, model=self._model, tokenizer=self._tokenizer, device=self.device)
        except Exception as e:
            self.last_error = f"pipeline({task_name}) failed: {e}"
            return None

    def _load_model(self) -> None:
        if self._loaded:
            return
        self._loaded = True

        if not TRANSFORMERS_AVAILABLE:
            self.available = False
            self.last_error = "transformers not installed"
            return

        try:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        except Exception as e:
            self.last_error = f"tokenizer/model load failed: {e}"
            self.available = False
            return

        for task in ("summarization", "text2text-generation", "any-to-any", "text-generation"):
            p = self._try_pipeline(task)
            if p is not None:
                self._pipeline = p
                break

        if not self._pipeline:
            self.available = False
            return

        try:
            test_input = "Summarize: Machine learning advances."
            out = self._pipeline(test_input, max_length=30, min_length=10, do_sample=False)
            if out:
                self.available = True
                self.last_error = None
            else:
                self.available = False
                self.last_error = "validation generation returned empty output"
        except Exception as e:
            self.available = False
            self.last_error = f"validation generation failed: {e}"

    def summarize(self, text: str, summary_type: str = "general") -> Optional[str]:
        if not self._loaded:
            self._load_model()
        if not self.available or not self._pipeline:
            return None
        try:
            if summary_type == "abstract":
                max_len = max(30, self.max_length - 20)
                min_len = max(10, self.min_length - 20)
            elif summary_type == "technical":
                max_len = self.max_length
                min_len = self.min_length
            else:
                max_len = self.max_length
                min_len = self.min_length
            truncated_text = " ".join(text.split()[:800])
            result = self._pipeline(truncated_text, max_length=max_len, min_length=min_len, do_sample=False)
            if isinstance(result, list) and result:
                first = result[0]
                if isinstance(first, dict):
                    return first.get("summary_text") or first.get("generated_text")
                return str(first)
            return None
        except Exception as e:
            self.last_error = f"summarize failed: {e}"
            return None

    def summarize_long(self, text: str, chunk_size: int = 500, num_chunks: int = 3) -> Optional[str]:
        if not self._loaded:
            self._load_model()
        if not self.available:
            return None
        words = text.split()
        chunk_words = max(50, int(chunk_size / 1.3))
        chunks = [" ".join(words[i:i+chunk_words]) for i in range(0, len(words), chunk_words)]
        summaries = []
        for c in chunks[:num_chunks]:
            s = self.summarize(c)
            if s:
                summaries.append(s)
        if not summaries:
            return None
        return self.summarize(" ".join(summaries))


class AcademicPaperSummarizer:
    """Specialized summarization for academic papers using fallback chain."""

    def __init__(self, device: int = -1):
        self.device = device
        self.primary = TransformerSummarizer(
            model_name="sshleifer/distilbart-cnn-12-6",
            max_length=150,
            min_length=50,
            device=device,
        )
        self.fallback = TransformerSummarizer(
            model_name="google/pegasus-arxiv",
            max_length=200,
            min_length=80,
            device=device,
        )
        self.secondary = TransformerSummarizer(
            model_name="t5-small",
            max_length=120,
            min_length=40,
            device=device,
        )

    @property
    def available(self) -> bool:
        return self.primary.available or self.fallback.available or self.secondary.available

    def summarize(self, text: str, summary_type: str = "general") -> Optional[str]:
        for model in (self.primary, self.fallback, self.secondary):
            if not model._loaded:
                model._load_model()
            if model.available:
                summary = model.summarize(text, summary_type)
                if summary:
                    return summary
        return None

    def create_summary_package(self, text: str) -> dict[str, Optional[str]]:
        return {
            "abstract": self.summarize(text, "abstract"),
            "methodology": self.summarize(text, "technical"),
            "results": self.summarize(text, "technical"),
        }
