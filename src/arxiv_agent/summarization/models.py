"""Domain models for summarization."""
from dataclasses import dataclass


@dataclass
class Summary:
    """Summary result."""
    paper_id: str
    title: str
    summary_text: str
