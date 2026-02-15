"""Collection domain models."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Paper:
    """arXiv paper data."""
    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    published: datetime
    categories: list[str]
    pdf_url: str
