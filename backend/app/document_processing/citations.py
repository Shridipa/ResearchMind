import re


_CITATION_PATTERNS = [
    re.compile(r"\((?:[A-Z][A-Za-z-]+(?: et al\.)?, \d{4}[a-z]?)\)"),
    re.compile(r"\[\d+(?:,\s*\d+)*\]"),
]


def extract_citations(text: str) -> list[str]:
    citations: set[str] = set()
    for pattern in _CITATION_PATTERNS:
        citations.update(match.group(0) for match in pattern.finditer(text))
    return sorted(citations)
