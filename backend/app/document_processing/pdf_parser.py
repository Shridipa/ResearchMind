from pathlib import Path
import re

import fitz

from app.core.errors import EmptyDocumentError
from app.document_processing.types import ParsedDocument, PageText


class PdfParser:
    _SECTION_REGEX = re.compile(r"^(abstract|summary|introduction|1\.?\s+introduction)\b", re.IGNORECASE)
    _AFFILIATION_KEYWORDS = re.compile(
        r"\b(university|institute|department|laboratory|college|school|company|inc|corp|ltd|research|center|centre)\b",
        re.IGNORECASE,
    )

    def parse(self, path: Path, paper_id: str, title: str | None = None) -> ParsedDocument:
        pages: list[PageText] = []
        with fitz.open(path) as doc:
            for page_index, page in enumerate(doc, start=1):
                text = page.get_text("text").strip()
                if text:
                    pages.append(PageText(page=page_index, text=text))
        if not pages:
            raise EmptyDocumentError("The uploaded PDF did not contain extractable text.")

        parsed_title, _, _ = self.extract_metadata(pages[0].text)
        document_title = title or parsed_title or path.stem
        return ParsedDocument(paper_id=paper_id, title=document_title, pages=pages)

    def extract_metadata(self, text: str) -> tuple[str | None, list[str], str | None]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        abstract = self._extract_abstract(lines)
        title, title_index = self._extract_title(lines)
        abstract_index = self._find_section_header(lines, ["abstract", "summary"])
        authors = self._extract_authors(lines, title_index, abstract_index)
        return title, authors, abstract

    def _find_section_header(self, lines: list[str], headers: list[str]) -> int | None:
        for index, line in enumerate(lines):
            normalized = line.strip().lower()
            for header in headers:
                if normalized.startswith(header):
                    return index
        return None

    def _extract_title(self, lines: list[str]) -> tuple[str | None, int]:
        candidate_lines = lines[:6]
        for index, line in enumerate(candidate_lines):
            if self._looks_like_title(line):
                return line, index
        return (candidate_lines[0], 0) if candidate_lines else (None, -1)

    def _looks_like_title(self, line: str) -> bool:
        if len(line.split()) < 3 or len(line.split()) > 18:
            return False
        if self._AFFILIATION_KEYWORDS.search(line):
            return False
        if re.search(r"@|doi:|http|www\.|\d{4}", line, re.IGNORECASE):
            return False
        return True

    def _extract_authors(self, lines: list[str], title_index: int, abstract_index: int | None) -> list[str]:
        authors: list[str] = []
        if title_index < 0:
            return authors

        end_index = abstract_index if abstract_index is not None else len(lines)
        candidate_lines = lines[title_index + 1 : end_index]

        for line in candidate_lines:
            if not line.strip():
                continue

            if self._SECTION_REGEX.match(line):
                break

            if self._AFFILIATION_KEYWORDS.search(line) and not self._looks_like_author_line(line):
                break

            if self._is_author_line(line):
                authors.extend(self._split_author_line(line))
                continue

            if authors:
                if self._looks_like_author_line(line):
                    authors.extend(self._split_author_line(line))
                    continue
                break

        normalized = [self._clean_author_name(author) for author in authors]
        return [name for name in normalized if name]

    def _is_author_line(self, line: str) -> bool:
        if self._AFFILIATION_KEYWORDS.search(line) and not self._looks_like_author_line(line):
            return False
        if re.search(r"@|doi:|http|www\.|\d{4}", line, re.IGNORECASE):
            return False
        return self._looks_like_author_line(line)

    def _looks_like_author_line(self, line: str) -> bool:
        lower = line.strip().lower()
        if re.search(r"\b(draft|version|submitted|copyright|preprint|contact|information|address|email|phone|fax|corresponding|authors’|authors')\b", lower):
            return False
        if ":" in line and not re.search(r"\band\b|,|;", line, re.IGNORECASE):
            return False

        words = [self._clean_author_name(word) for word in line.split()]
        words = [word for word in words if word]
        if len(words) < 2 or len(words) > 12:
            return False

        name_like = 0
        for word in words:
            if re.match(r"^[A-Z][a-z]+(?:[-'][A-Z][a-z]+)?$", word):
                name_like += 1
            elif re.match(r"^[A-Z][a-z]+\.$", word):
                name_like += 1

        if name_like < 2:
            return False

        if self._AFFILIATION_KEYWORDS.search(line):
            return False

        return True

    def _split_author_line(self, line: str) -> list[str]:
        parts = re.split(r",|;|\band\b|\band\b", line)
        return [self._clean_author_name(part) for part in parts if self._clean_author_name(part)]

    def _clean_author_name(self, author: str) -> str:
        author = author.strip()
        # Remove trailing footnote markers and affiliation punctuation
        author = re.sub(r"[\*†‡\d]+$", "", author).strip()
        author = re.sub(r"\s*\(.*?\)\s*$", "", author).strip()
        author = author.strip(" ,;.*")
        if not author:
            return author

        # Remove single trailing symbol markers
        author = re.sub(r"[\*†‡]+$", "", author).strip()
        return author

    def _extract_abstract(self, lines: list[str]) -> str | None:
        abstract_index = self._find_section_header(lines, ["abstract", "summary"])
        if abstract_index is None:
            return None

        first_line = lines[abstract_index]
        abstract_lines: list[str] = []
        inline_match = re.match(r"^(?:abstract|summary)[:\-\s]*([^\n]+)$", first_line, re.IGNORECASE)
        if inline_match and inline_match.group(1).strip():
            abstract_lines.append(inline_match.group(1).strip())

        for line in lines[abstract_index + 1 :]:
            if self._SECTION_REGEX.match(line):
                break
            if not line:
                if abstract_lines:
                    break
                continue
            abstract_lines.append(line)

        return " ".join(abstract_lines).strip() or None
