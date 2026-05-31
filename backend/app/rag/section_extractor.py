"""Extract research paper sections for comparison analysis."""

from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class PaperSection:
    """A section from a research paper."""
    section_name: str  # abstract, introduction, methodology, results, etc.
    content: str
    page_range: Optional[tuple[int, int]] = None
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SectionExtractor:
    """
    Extract major sections from research papers.
    
    Identifies: abstract, introduction, methodology, results, 
    discussion, related work, conclusion, references
    """
    
    # Common section headers (case-insensitive)
    SECTION_PATTERNS = {
        "abstract": r"^(abstract|summary)[\s]*$",
        "introduction": r"^(1\.?\s+)?introduction[\s]*$",
        "related_work": r"^(2\.?\s+)?(related\s+work|background|prior\s+work|literature\s+review)[\s]*$",
        "methodology": r"^(3\.?\s+)?(methodology|method|approach|techniques|proposed\s+method)[\s]*$",
        "results": r"^(4\.?\s+)?(results|experiments|evaluation|experimental\s+results)[\s]*$",
        "discussion": r"^(discussion|analysis)[\s]*$",
        "conclusion": r"^(conclusion|conclusions|future\s+work)[\s]*$",
        "references": r"^(references|bibliography|citations)[\s]*$",
        "appendix": r"^(appendix|appendices|supplementary\s+material)[\s]*$",
    }
    
    def __init__(self):
        self.compiled_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.SECTION_PATTERNS.items()
        }
    
    def extract_sections(self, text: str) -> dict[str, PaperSection]:
        """
        Extract all major sections from paper text.
        
        Args:
            text: Full paper text
        
        Returns:
            Dict mapping section names to PaperSection objects
        """
        sections = {}
        lines = text.split("\n")
        
        current_section = "preamble"
        section_content = []
        section_start_line = 0
        
        for i, line in enumerate(lines):
            # Check if this line is a section header
            detected_section = self._detect_section_header(line)
            
            if detected_section:
                # Save previous section
                if section_content:
                    sections[current_section] = PaperSection(
                        section_name=current_section,
                        content="\n".join(section_content).strip(),
                        page_range=(section_start_line, i - 1),
                    )
                
                # Start new section
                current_section = detected_section
                section_content = []
                section_start_line = i + 1
            else:
                section_content.append(line)
        
        # Save final section
        if section_content:
            sections[current_section] = PaperSection(
                section_name=current_section,
                content="\n".join(section_content).strip(),
                page_range=(section_start_line, len(lines)),
            )
        
        return sections
    
    def _detect_section_header(self, line: str) -> Optional[str]:
        """
        Detect if line is a section header.
        
        Returns:
            Section name if detected, None otherwise
        """
        line_stripped = line.strip()
        
        # Skip empty lines and short lines
        if not line_stripped or len(line_stripped) > 100:
            return None
        
        # Check against patterns
        for section_name, pattern in self.compiled_patterns.items():
            if pattern.match(line_stripped):
                return section_name
        
        return None
    
    def extract_abstract(self, text: str) -> Optional[str]:
        """Extract abstract section."""
        sections = self.extract_sections(text)
        section = sections.get("abstract")
        return section.content if section else None
    
    def extract_methodology(self, text: str) -> Optional[str]:
        """Extract methodology section."""
        sections = self.extract_sections(text)
        section = sections.get("methodology")
        return section.content if section else None
    
    def extract_results(self, text: str) -> Optional[str]:
        """Extract results section."""
        sections = self.extract_sections(text)
        section = sections.get("results")
        return section.content if section else None
    
    def extract_key_sections(self, text: str) -> dict[str, str]:
        """Extract key sections for comparison."""
        sections = self.extract_sections(text)
        
        key_sections = {}
        for key in ["abstract", "methodology", "results", "discussion"]:
            if key in sections:
                key_sections[key] = sections[key].content
        
        return key_sections
    
    def summarize_sections(self, text: str) -> dict[str, str]:
        """Get brief summary of each section."""
        sections = self.extract_sections(text)
        
        summaries = {}
        for name, section in sections.items():
            # Get first 3 sentences as preview
            sentences = section.content.split(". ")[:3]
            summary = ". ".join(sentences)
            if not summary.endswith("."):
                summary += "."
            summaries[name] = summary[:200]  # Truncate to 200 chars
        
        return summaries


class ResearchPaperExtractor:
    """Specialized extractor for academic research papers."""
    
    def __init__(self):
        self.section_extractor = SectionExtractor()
    
    def extract_methodology_details(self, text: str) -> dict:
        """Extract specific methodology details."""
        methodology = self.section_extractor.extract_methodology(text)
        if not methodology:
            return {}
        
        return {
            "full_text": methodology,
            "mentions_neural": "neural" in methodology.lower(),
            "mentions_experimental": "experiment" in methodology.lower(),
            "mentions_computational": any(
                term in methodology.lower()
                for term in ["algorithm", "computation", "complexity"]
            ),
        }
    
    def extract_results_metrics(self, text: str) -> dict:
        """Extract results and metrics mentioned."""
        results = self.section_extractor.extract_results(text)
        if not results:
            return {}
        
        # Find numeric metrics (accuracy, F1, BLEU, etc.)
        metrics = {}
        metric_patterns = {
            "accuracy": r"accuracy[:\s]+([0-9.]+)%?",
            "f1": r"f1[-\s]score[:\s]+([0-9.]+)",
            "bleu": r"bleu[:\s]+([0-9.]+)",
            "rouge": r"rouge[:\s]+([0-9.]+)",
            "rmse": r"rmse[:\s]+([0-9.]+)",
            "auc": r"auc[:\s]+([0-9.]+)",
        }
        
        for metric_name, pattern in metric_patterns.items():
            matches = re.finditer(pattern, results, re.IGNORECASE)
            for match in matches:
                metrics[metric_name] = match.group(1)
        
        return {
            "full_text": results,
            "mentioned_metrics": metrics,
            "mentions_sota": "state-of-the-art" in results.lower() or "sota" in results.lower(),
        }
    
    def extract_related_work(self, text: str) -> Optional[str]:
        """Extract related work/background section."""
        return self.section_extractor.extract_sections(text).get("related_work", PaperSection("", "")).content
    
    def extract_conclusion(self, text: str) -> Optional[str]:
        """Extract conclusion section."""
        return self.section_extractor.extract_sections(text).get("conclusion", PaperSection("", "")).content
    
    def get_paper_summary(self, text: str) -> dict:
        """Get comprehensive paper summary."""
        sections = self.section_extractor.extract_sections(text)
        
        return {
            "abstract": sections.get("abstract", PaperSection("", "")).content[:500],
            "methodology": self.extract_methodology_details(text),
            "results": self.extract_results_metrics(text),
            "conclusion": sections.get("conclusion", PaperSection("", "")).content[:300],
            "section_count": len(sections),
        }


class SectionComparator:
    """Compare sections from multiple papers."""
    
    def __init__(self):
        self.extractor = ResearchPaperExtractor()
    
    def compare_methodologies(
        self,
        text1: str,
        text2: str,
    ) -> dict:
        """Compare methodology sections."""
        details1 = self.extractor.extract_methodology_details(text1)
        details2 = self.extractor.extract_methodology_details(text2)
        
        return {
            "paper1_methodology": details1,
            "paper2_methodology": details2,
            "similarities": {
                "both_neural": details1.get("mentions_neural") and details2.get("mentions_neural"),
                "both_experimental": details1.get("mentions_experimental") and details2.get("mentions_experimental"),
            },
            "differences": {
                "one_neural": details1.get("mentions_neural") != details2.get("mentions_neural"),
                "one_experimental": details1.get("mentions_experimental") != details2.get("mentions_experimental"),
            },
        }
    
    def compare_results(
        self,
        text1: str,
        text2: str,
    ) -> dict:
        """Compare results sections."""
        results1 = self.extractor.extract_results_metrics(text1)
        results2 = self.extractor.extract_results_metrics(text2)
        
        # Compare metrics if they exist
        metrics_comparison = {}
        common_metrics = set(results1.get("mentioned_metrics", {}).keys()) & set(
            results2.get("mentioned_metrics", {}).keys()
        )
        
        for metric in common_metrics:
            try:
                val1 = float(results1["mentioned_metrics"][metric])
                val2 = float(results2["mentioned_metrics"][metric])
                metrics_comparison[metric] = {
                    "paper1": val1,
                    "paper2": val2,
                    "difference": val2 - val1,
                    "paper_with_better": "paper2" if val2 > val1 else "paper1",
                }
            except (ValueError, KeyError):
                pass
        
        return {
            "paper1_results": results1,
            "paper2_results": results2,
            "metrics_comparison": metrics_comparison,
            "paper1_mentions_sota": results1.get("mentions_sota"),
            "paper2_mentions_sota": results2.get("mentions_sota"),
        }
