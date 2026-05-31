from dataclasses import dataclass


@dataclass(frozen=True)
class PageText:
    page: int
    text: str


@dataclass(frozen=True)
class ParsedDocument:
    paper_id: str
    title: str
    pages: list[PageText]
