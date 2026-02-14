from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from src.collector import collect_papers
from src.config import SearchConfig


class TestCollectPapersQueryBuilding:
    """collect_papers が正しいクエリを構築して arxiv.Search に渡すことを検証する。"""

    def test_single_category_single_keyword(self, mocker: pytest.fixture) -> None:
        mock_client = MagicMock()
        mock_client.results.return_value = []
        mocker.patch("src.collector.arxiv.Client", return_value=mock_client)
        mock_search = mocker.patch("src.collector.arxiv.Search")

        config = SearchConfig(
            categories=["cs.AI"],
            keywords=["LLM"],
            max_results=10,
        )
        collect_papers(config)

        mock_search.assert_called_once()
        query = mock_search.call_args.kwargs["query"]
        assert query == "(cat:cs.AI) AND ((ti:LLM OR abs:LLM))"

    def test_multiple_categories_multiple_keywords(
        self, mocker: pytest.fixture
    ) -> None:
        mock_client = MagicMock()
        mock_client.results.return_value = []
        mocker.patch("src.collector.arxiv.Client", return_value=mock_client)
        mock_search = mocker.patch("src.collector.arxiv.Search")

        config = SearchConfig(
            categories=["cs.AI", "cs.CL"],
            keywords=["LLM", "transformer"],
            max_results=5,
        )
        collect_papers(config)

        query = mock_search.call_args.kwargs["query"]
        assert query == (
            "(cat:cs.AI OR cat:cs.CL) AND "
            "((ti:LLM OR abs:LLM) OR (ti:transformer OR abs:transformer))"
        )


class TestCollectPapers:
    def _make_mock_result(
        self,
        entry_id: str,
        title: str,
        summary: str,
        author_names: list[str],
    ) -> MagicMock:
        result = MagicMock()
        result.entry_id = entry_id
        result.title = title
        result.summary = summary
        result.published = datetime(2025, 1, 15, tzinfo=timezone.utc)

        authors = []
        for name in author_names:
            author = MagicMock()
            author.name = name
            authors.append(author)
        result.authors = authors

        return result

    def test_returns_papers_from_arxiv_results(self, mocker: pytest.fixture) -> None:
        mock_result = self._make_mock_result(
            entry_id="http://arxiv.org/abs/2501.00001v1",
            title="Test Paper",
            summary="This is a test abstract.",
            author_names=["Alice", "Bob"],
        )

        mock_client = MagicMock()
        mock_client.results.return_value = [mock_result]
        mocker.patch("src.collector.arxiv.Client", return_value=mock_client)
        mocker.patch("src.collector.arxiv.Search")

        config = SearchConfig(
            categories=["cs.AI"],
            keywords=["LLM"],
            max_results=10,
        )
        papers = collect_papers(config)

        assert len(papers) == 1
        assert papers[0].arxiv_id == "http://arxiv.org/abs/2501.00001v1"
        assert papers[0].title == "Test Paper"
        assert papers[0].abstract == "This is a test abstract."
        assert papers[0].authors == ["Alice", "Bob"]
        assert papers[0].url == "http://arxiv.org/abs/2501.00001v1"

    def test_returns_empty_list_when_no_results(
        self, mocker: pytest.fixture
    ) -> None:
        mock_client = MagicMock()
        mock_client.results.return_value = []
        mocker.patch("src.collector.arxiv.Client", return_value=mock_client)
        mocker.patch("src.collector.arxiv.Search")

        config = SearchConfig(
            categories=["cs.AI"],
            keywords=["LLM"],
            max_results=10,
        )
        papers = collect_papers(config)
        assert papers == []

    def test_multiple_results(self, mocker: pytest.fixture) -> None:
        results = [
            self._make_mock_result(
                entry_id=f"http://arxiv.org/abs/2501.0000{i}v1",
                title=f"Paper {i}",
                summary=f"Abstract {i}",
                author_names=[f"Author{i}"],
            )
            for i in range(3)
        ]

        mock_client = MagicMock()
        mock_client.results.return_value = results
        mocker.patch("src.collector.arxiv.Client", return_value=mock_client)
        mocker.patch("src.collector.arxiv.Search")

        config = SearchConfig(
            categories=["cs.AI"],
            keywords=["LLM"],
            max_results=10,
        )
        papers = collect_papers(config)

        assert len(papers) == 3
        for i, paper in enumerate(papers):
            assert paper.title == f"Paper {i}"
