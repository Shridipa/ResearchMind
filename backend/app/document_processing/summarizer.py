"""Unified local summarization engine with smart API fallback."""

import json
from pathlib import Path
from typing import Optional

from app.document_processing.extractive import ResearchPaperExtractor
from app.document_processing.transformer_summary import AcademicPaperSummarizer


class LocalSummarizer:
    """
    Local-first research summarization engine.
    
    Pipeline:
    1. Try extractive summarization (always works, fast)
    2. Try transformer summarization (better quality if available)
    3. Fall back to API if specified (for complex queries)
    
    This dramatically reduces OpenRouter API calls.
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize local summarizer.
        
        Args:
            cache_dir: Directory to cache summaries
        """
        self.extractive = ResearchPaperExtractor()
        self.transformer = AcademicPaperSummarizer(device=-1)  # CPU
        self.cache_dir = cache_dir
        
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, paper_id: str, summary_type: str) -> Path:
        """Get cache path for a summary."""
        if not self.cache_dir:
            return None
        return self.cache_dir / f"{paper_id}_{summary_type}.json"
    
    def _load_cache(self, paper_id: str, summary_type: str) -> Optional[dict]:
        """Load cached summary."""
        cache_path = self._get_cache_path(paper_id, summary_type)
        if cache_path and cache_path.exists():
            try:
                return json.loads(cache_path.read_text())
            except Exception:
                return None
        return None
    
    def _save_cache(self, paper_id: str, summary_type: str, summary: dict):
        """Save summary to cache."""
        cache_path = self._get_cache_path(paper_id, summary_type)
        if cache_path:
            try:
                cache_path.write_text(json.dumps(summary, indent=2))
            except Exception:
                pass  # Fail silently
    
    def summarize_abstract(
        self,
        text: str,
        paper_id: Optional[str] = None,
        use_transformer: bool = True,
    ) -> str:
        """
        Generate concise abstract/summary.
        
        Args:
            text: Text to summarize
            paper_id: Optional paper ID for caching
            use_transformer: Try transformer model
        
        Returns:
            Summary text
        """
        # Check cache
        if paper_id:
            cached = self._load_cache(paper_id, "abstract")
            if cached:
                return cached.get("text", "")
        
        # Try transformer first
        if use_transformer and self.transformer.available:
            summary = self.transformer.summarize(text, "abstract")
            if summary:
                if paper_id:
                    self._save_cache(paper_id, "abstract", {"text": summary})
                return summary
        
        # Fallback to extractive
        summary = self.extractive.text_summarizer.summarize(text, num_sentences=4)
        
        if paper_id:
            self._save_cache(paper_id, "abstract", {"text": summary})
        
        return summary
    
    def summarize_paper(
        self,
        text: str,
        paper_id: Optional[str] = None,
    ) -> dict[str, str]:
        """
        Generate comprehensive paper summary with sections.
        
        Args:
            text: Paper text
            paper_id: Optional paper ID for caching
        
        Returns:
            Dict with contributions, methodology, results, limitations
        """
        # Check cache
        if paper_id:
            cached = self._load_cache(paper_id, "full")
            if cached:
                return cached
        
        summary = {}
        
        # Contribution (prefer transformer if available)
        if self.transformer.available:
            contrib_text = self.transformer.summarize(text[:2000], "abstract")
            summary["contributions"] = contrib_text or self.extractive.extract_contribution(text)
        else:
            summary["contributions"] = self.extractive.extract_contribution(text)
        
        # Methodology
        if self.transformer.available:
            method_text = self.transformer.summarize(text[500:2500], "technical")
            summary["methodology"] = method_text or self.extractive.extract_methodology(text)
        else:
            summary["methodology"] = self.extractive.extract_methodology(text)
        
        # Results
        if self.transformer.available:
            results_text = self.transformer.summarize(text[1500:3500], "technical")
            summary["results"] = results_text or self.extractive.extract_results(text)
        else:
            summary["results"] = self.extractive.extract_results(text)
        
        # Limitations (extractive only, usually explicit)
        limitations = self.extractive.extract_limitations(text)
        summary["limitations"] = " ".join(limitations) if limitations else "Not explicitly mentioned."
        
        # Cache
        if paper_id:
            self._save_cache(paper_id, "full", summary)
        
        return summary
    
    def get_summary_mode(self) -> str:
        """
        Get current summarization mode.
        
        Returns:
            'transformer' if models loaded, else 'extractive'
        """
        if self.transformer.available:
            return "transformer"
        return "extractive"
    
    def get_summary_stats(self) -> dict[str, str | bool]:
        """Get summarizer capabilities."""
        return {
            "mode": self.get_summary_mode(),
            "transformer_available": self.transformer.primary.available,
            "cached": bool(self.cache_dir),
            "cache_directory": str(self.cache_dir) if self.cache_dir else None,
        }


class SummarizationResult:
    """Result from summarization with metadata."""
    
    def __init__(
        self,
        summary: str,
        mode: str = "extractive",
        tokens_saved: int = 0,
        api_calls_avoided: int = 1,
    ):
        self.summary = summary
        self.mode = mode  # "extractive", "transformer", "api"
        self.tokens_saved = tokens_saved
        self.api_calls_avoided = api_calls_avoided
    
    def to_dict(self) -> dict:
        """Convert to dict for API response."""
        return {
            "summary": self.summary,
            "mode": self.mode,
            "tokens_saved": self.tokens_saved,
            "api_calls_avoided": self.api_calls_avoided,
        }


def estimate_api_cost_saved(
    text_length: int,
    num_summaries: int = 1,
    avg_tokens_per_call: int = 500,
    cost_per_1k_tokens: float = 0.001,  # Approximate
) -> dict[str, float]:
    """
    Estimate API costs saved by using local summarization.
    
    Args:
        text_length: Total characters in input
        num_summaries: Number of summaries generated
        avg_tokens_per_call: Tokens per API call (roughly char/4)
        cost_per_1k_tokens: Cost per 1000 tokens
    
    Returns:
        Dict with estimated costs and savings
    """
    # Rough token estimation: 1 token ≈ 4 characters
    estimated_api_tokens = (text_length / 4) * num_summaries
    estimated_cost = (estimated_api_tokens / 1000) * cost_per_1k_tokens
    
    return {
        "estimated_tokens": estimated_api_tokens,
        "estimated_cost_usd": estimated_cost,
        "api_calls_avoided": num_summaries,
    }
