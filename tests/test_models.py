from datetime import datetime, timezone

import pytest

from src.models import Paper, SummarizedPaper


def _valid_paper_kwargs() -> dict:
    return {
        "arxiv_id": "http://arxiv.org/abs/2501.00001v1",
        "title": "Test Paper",
        "abstract": "Test abstract",
        "authors": ["Alice"],
        "published": datetime(2025, 1, 15, tzinfo=timezone.utc),
        "url": "http://arxiv.org/abs/2501.00001v1",
    }


class TestPaper:
    def test_valid_paper(self) -> None:
        paper = Paper(**_valid_paper_kwargs())
        assert paper.arxiv_id == "http://arxiv.org/abs/2501.00001v1"
        assert paper.title == "Test Paper"

    def test_is_frozen(self) -> None:
        paper = Paper(**_valid_paper_kwargs())
        with pytest.raises(AttributeError):
            paper.title = "New Title"  # type: ignore[misc]

    def test_empty_arxiv_id_raises(self) -> None:
        kwargs = _valid_paper_kwargs()
        kwargs["arxiv_id"] = ""
        with pytest.raises(ValueError, match="arxiv_id is required"):
            Paper(**kwargs)

    def test_empty_title_raises(self) -> None:
        kwargs = _valid_paper_kwargs()
        kwargs["title"] = ""
        with pytest.raises(ValueError, match="title is required"):
            Paper(**kwargs)

    def test_empty_abstract_raises(self) -> None:
        kwargs = _valid_paper_kwargs()
        kwargs["abstract"] = ""
        with pytest.raises(ValueError, match="abstract is required"):
            Paper(**kwargs)

    def test_empty_authors_raises(self) -> None:
        kwargs = _valid_paper_kwargs()
        kwargs["authors"] = []
        with pytest.raises(ValueError, match="authors is required"):
            Paper(**kwargs)

    def test_empty_url_raises(self) -> None:
        kwargs = _valid_paper_kwargs()
        kwargs["url"] = ""
        with pytest.raises(ValueError, match="url is required"):
            Paper(**kwargs)


class TestSummarizedPaper:
    def test_valid_summarized_paper(self) -> None:
        paper = Paper(**_valid_paper_kwargs())
        summarized = SummarizedPaper(paper=paper, summary="日本語の要約")
        assert summarized.summary == "日本語の要約"
        assert summarized.paper == paper

    def test_empty_summary_raises(self) -> None:
        paper = Paper(**_valid_paper_kwargs())
        with pytest.raises(ValueError, match="summary is required"):
            SummarizedPaper(paper=paper, summary="")
