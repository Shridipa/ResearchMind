"""Extractive summarization using frequency-based and TextRank approaches."""

import re
from collections import defaultdict

import numpy as np


class ExtractiveTextSummarizer:
    """
    Extractive summarization using frequency-based sentence ranking.
    
    Approaches:
    - TF-IDF based sentence scoring
    - TextRank-inspired graph-based ranking
    - Sentence position bias
    """
    
    def __init__(self, window_size: int = 5):
        """
        Initialize extractive summarizer.
        
        Args:
            window_size: Context window for co-occurrence scores
        """
        self.window_size = window_size
    
    def summarize(
        self,
        text: str,
        num_sentences: int = 5,
        min_sentence_length: int = 10,
    ) -> str:
        """
        Extract key sentences from text.
        
        Args:
            text: Input text to summarize
            num_sentences: Number of sentences to extract
            min_sentence_length: Minimum words in a sentence
        
        Returns:
            Extracted summary (sentences in original order)
        """
        # Split into sentences
        sentences = self._split_sentences(text)
        
        # Filter short sentences
        sentences = [s for s in sentences if len(s.split()) >= min_sentence_length]
        
        if len(sentences) <= num_sentences:
            return " ".join(sentences)
        
        # Score sentences
        scores = self._score_sentences(sentences)
        
        # Get top-k sentences while preserving order
        top_indices = np.argsort(scores)[-num_sentences:]
        top_indices = sorted(top_indices)  # Preserve original order
        
        summary = " ".join(sentences[i] for i in top_indices)
        return summary
    
    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Handle abbreviations and common cases
        text = re.sub(r'(?<=[a-z])\. (?=[A-Z])', '._PERIOD_', text)
        text = re.sub(r'(?<=[A-Z])\. (?=[A-Z])', '._PERIOD_', text)
        
        # Split on periods, exclamation, question marks
        sentences = re.split(r'[.!?]+', text)
        
        # Restore and clean
        sentences = [
            s.replace('_PERIOD_', '.').strip()
            for s in sentences
            if s.strip()
        ]
        
        return sentences
    
    def _score_sentences(self, sentences: list[str]) -> np.ndarray:
        """Score sentences using TF-IDF and position bias."""
        if not sentences:
            return np.array([])
        
        # Extract words
        word_freq = defaultdict(int)
        sentence_words = []
        
        for sentence in sentences:
            words = self._tokenize(sentence)
            sentence_words.append(set(words))
            for word in words:
                word_freq[word] += 1
        
        # Remove stop words
        stop_words = self._get_stop_words()
        word_freq = {w: f for w, f in word_freq.items() if w not in stop_words}
        
        if not word_freq:
            # Fallback: score by position
            return np.array([1.0 / (i + 1) for i in range(len(sentences))])
        
        # Normalize frequencies
        max_freq = max(word_freq.values())
        word_freq = {w: f / max_freq for w, f in word_freq.items()}
        
        # Score sentences
        scores = np.zeros(len(sentences))
        
        for i, words in enumerate(sentence_words):
            # TF-IDF score
            tf_idf = sum(word_freq.get(w, 0) for w in words) / max(len(words), 1)
            scores[i] = tf_idf
            
            # Position bias (first sentences ranked higher)
            position_score = 1.0 / (1.0 + 0.1 * i)
            scores[i] = 0.7 * tf_idf + 0.3 * position_score
        
        return scores
    
    def _tokenize(self, text: str) -> list[str]:
        """Tokenize and clean text."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation but keep hyphenated words
        words = re.findall(r'\b\w+(?:-\w+)?\b', text)
        
        return words
    
    def _get_stop_words(self) -> set[str]:
        """Common English stop words."""
        return {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'that',
            'the', 'to', 'was', 'will', 'with', 'this', 'have', 'had',
            'but', 'they', 'what', 'when', 'where', 'who', 'which', 'why',
            'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'so', 'than', 'too', 'very', 'can', 'just', 'now', 'being'
        }


class ResearchPaperExtractor:
    """
    Extract key information from research papers using section-aware extraction.
    """
    
    def __init__(self):
        self.text_summarizer = ExtractiveTextSummarizer()
        self.section_patterns = {
            "abstract": r"^(abstract|summary)[\s]*$",
            "intro": r"^(introduction|1[\.\s]+introduction|background|overview)[\s]*$",
            "methodology": r"^(methodology|method|approach|framework|implementation|experimental setup|proposed|3[\.\s]+)[\s]*$",
            "results": r"^(results|experiments|evaluation|findings|analysis|4[\.\s]+)[\s]*$",
            "conclusion": r"^(conclusion|conclusions|future work|discussion|5[\.\s]+)[\s]*$",
            "related": r"^(related work|background|literature|prior work|2[\.\s]+)[\s]*$",
        }
        self._negative_contribution_patterns = [
            r"organized as follows",
            r"rest of the paper",
            r"paper is organized",
            r"in this paper",
        ]
    
    def _find_section_boundaries(self, text: str) -> dict[str, tuple[int, int]]:
        """Find start/end indices of major sections."""
        lines = text.split("\n")
        boundaries = {}
        section_starts = {}

        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            for section, pattern in self.section_patterns.items():
                if re.match(pattern, line_lower):
                    section_starts[section] = i
                    break

        sorted_sections = sorted(section_starts.items(), key=lambda x: x[1])
        for idx, (section, start) in enumerate(sorted_sections):
            end = sorted_sections[idx + 1][1] if idx + 1 < len(sorted_sections) else len(lines)
            boundaries[section] = (start, end)

        return boundaries

    def _get_section_text(self, text: str, section_names: list[str]) -> str | None:
        sections = self._find_section_boundaries(text)
        for name in section_names:
            if name in sections:
                start, end = sections[name]
                lines = text.split("\n")[start:end]
                section_text = "\n".join(lines).strip()
                if section_text:
                    return section_text
        return None

    def _score_sentence(self, sentence: str, keywords: list[tuple[str, int]]) -> float:
        score = 0.0
        sentence_lower = sentence.lower()
        for kw, weight in keywords:
            if kw in sentence_lower:
                score += weight

        for pattern in self._negative_contribution_patterns:
            if re.search(pattern, sentence_lower):
                score -= 4

        if sentence_lower.startswith("we ") or sentence_lower.startswith("our "):
            score += 1

        return score

    def _filter_sentences(self, sentences: list[str]) -> list[str]:
        filtered = []
        for sentence in sentences:
            if len(sentence.split()) < 6:
                continue
            if re.search(r"^(in this paper|this paper|the rest of the paper|we also)", sentence.strip().lower()):
                continue
            filtered.append(sentence)
        return filtered
    
    def extract_contribution(self, text: str, num_sentences: int = 3) -> str:
        """Extract main contribution from paper using section awareness."""
        section_text = self._get_section_text(text, ["abstract", "intro", "related", "conclusion"])
        search_text = section_text if section_text else text

        contribution_keywords = [
            ('propose', 4), ('introduce', 4), ('present', 3), ('develop', 3), ('novel', 4),
            ('contribution', 5), ('key contribution', 6), ('main contribution', 6),
            ('new', 2), ('approach', 3), ('framework', 3), ('model', 2), ('algorithm', 3),
            ('we propose', 4), ('we introduce', 4), ('we present', 4), ('we develop', 3),
            ('our approach', 4), ('our model', 3), ('our method', 3),
        ]

        sentences = self._filter_sentences(self.text_summarizer._split_sentences(search_text))
        if not sentences:
            sentences = self.text_summarizer._split_sentences(text)

        scores = [self._score_sentence(sentence, contribution_keywords) for sentence in sentences]
        if not scores or max(scores) <= 0:
            return " ".join(sentences[:num_sentences])

        top_indices = np.argsort(scores)[-num_sentences:]
        top_indices = sorted(top_indices)
        return " ".join(sentences[i] for i in top_indices)
    
    def extract_methodology(self, text: str, num_sentences: int = 3) -> str:
        """Extract methodology using section detection."""
        section_text = self._get_section_text(text, ["methodology", "results", "intro", "abstract"])
        search_text = section_text if section_text else text

        method_keywords = [
            ('method', 3), ('approach', 3), ('algorithm', 3), ('technique', 3),
            ('framework', 3), ('implementation', 3), ('training', 2), ('dataset', 2),
            ('experiment', 2), ('evaluate', 2), ('we', 1), ('our', 1),
            ('propose', 2), ('use', 1), ('model', 2), ('design', 2),
        ]

        sentences = self._filter_sentences(self.text_summarizer._split_sentences(search_text))
        if not sentences:
            sentences = self.text_summarizer._split_sentences(text[500:2500])

        scores = [self._score_sentence(sentence, method_keywords) for sentence in sentences]
        if not scores or max(scores) <= 0:
            return " ".join(sentences[:num_sentences])

        top_indices = np.argsort(scores)[-num_sentences:]
        top_indices = sorted(top_indices)
        return " ".join(sentences[i] for i in top_indices)
    
    def extract_limitations(self, text: str, num_sentences: int = 2) -> list[str]:
        """Extract limitations mentioned in paper."""
        limitation_keywords = [
            'limitation', 'limited', 'restrict', 'challenge', 'difficult', 'complex',
            'scalability', 'compute', 'future work', 'open', 'further research',
        ]
        
        sentences = self.text_summarizer._split_sentences(text)
        extracted = []
        
        for sentence in sentences:
            if any(kw in sentence.lower() for kw in limitation_keywords):
                extracted.append(sentence)
        
        return extracted[:num_sentences]
    
    def extract_results(self, text: str, num_sentences: int = 3) -> str:
        """Extract key results from paper."""
        result_keywords = [
            ('result', 2), ('show', 1), ('achieve', 2), ('outperform', 2), ('accuracy', 2),
            ('performance', 2), ('improve', 2), ('better', 1), ('sota', 3), ('state-of-the-art', 3),
            ('benchmark', 2), ('metric', 1), ('score', 1), ('evaluated', 1), ('demonstrate', 1),
        ]
        
        sentences = self.text_summarizer._split_sentences(text)
        if not sentences:
            return text[1500:2200]
        
        scores = []
        for sentence in sentences:
            score = sum(weight for kw, weight in result_keywords if kw in sentence.lower())
            scores.append(score)
        
        if not scores or max(scores) == 0:
            return " ".join(sentences[:num_sentences])
        
        top_indices = np.argsort(scores)[-num_sentences:]
        top_indices = sorted(top_indices)
        
        return " ".join(sentences[i] for i in top_indices)
