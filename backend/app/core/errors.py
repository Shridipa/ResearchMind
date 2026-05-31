class ResearchMindError(Exception):
    """Base exception for domain failures."""


class EmptyDocumentError(ResearchMindError):
    """Raised when a parsed document contains no usable text."""


class RetrievalError(ResearchMindError):
    """Raised when retrieval cannot be completed."""
