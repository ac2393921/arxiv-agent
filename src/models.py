from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Paper:
    arxiv_id: str
    title: str
    abstract: str
    authors: list[str]
    published: datetime
    url: str

    def __post_init__(self) -> None:
        if not self.arxiv_id:
            raise ValueError("arxiv_id is required")
        if not self.title:
            raise ValueError("title is required")
        if not self.abstract:
            raise ValueError("abstract is required")
        if not self.authors:
            raise ValueError("authors is required")
        if not self.url:
            raise ValueError("url is required")


@dataclass(frozen=True)
class SummarizedPaper:
    paper: Paper
    summary: str

    def __post_init__(self) -> None:
        if not self.summary:
            raise ValueError("summary is required")
