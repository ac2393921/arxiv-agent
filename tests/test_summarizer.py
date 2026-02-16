import os
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from src.config import SummaryConfig
from src.models import Paper
from src.summarizer import summarize_papers


def _make_paper(title: str, abstract: str) -> Paper:
    return Paper(
        arxiv_id="http://arxiv.org/abs/2501.00001v1",
        title=title,
        abstract=abstract,
        authors=["Alice"],
        published=datetime(2025, 1, 15, tzinfo=timezone.utc),
        url="http://arxiv.org/abs/2501.00001v1",
    )


SUMMARY_CONFIG = SummaryConfig(
    prompt_template="Title: {title}\nAuthors: {authors}\nAbstract: {abstract}\nSummarize in Japanese.",
)


class TestSummarizePapers:
    def test_summarizes_single_paper(self, mocker: pytest.fixture) -> None:
        mocker.patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
        mocker.patch("src.summarizer.time.sleep")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "日本語の要約"
        mock_client.models.generate_content.return_value = mock_response
        mocker.patch("src.summarizer.genai.Client", return_value=mock_client)

        paper = _make_paper("Test Paper", "Test abstract")
        results = summarize_papers([paper], SUMMARY_CONFIG)

        assert len(results) == 1
        assert results[0].paper == paper
        assert results[0].summary == "日本語の要約"

    def test_summarizes_multiple_papers_with_sleep(
        self, mocker: pytest.fixture
    ) -> None:
        mocker.patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
        mock_sleep = mocker.patch("src.summarizer.time.sleep")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "要約"
        mock_client.models.generate_content.return_value = mock_response
        mocker.patch("src.summarizer.genai.Client", return_value=mock_client)

        papers = [_make_paper(f"Paper {i}", f"Abstract {i}") for i in range(3)]
        results = summarize_papers(papers, SUMMARY_CONFIG)

        assert len(results) == 3
        # sleep is called between papers (not before first)
        assert mock_sleep.call_count == 2

    def test_raises_when_api_key_missing(self, mocker: pytest.fixture) -> None:
        mocker.patch.dict(os.environ, {}, clear=True)

        paper = _make_paper("Test", "Abstract")
        with pytest.raises(
            RuntimeError, match="GEMINI_API_KEY environment variable is not set"
        ):
            summarize_papers([paper], SUMMARY_CONFIG)

    def test_formats_prompt_with_paper_data(self, mocker: pytest.fixture) -> None:
        mocker.patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
        mocker.patch("src.summarizer.time.sleep")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "要約"
        mock_client.models.generate_content.return_value = mock_response
        mocker.patch("src.summarizer.genai.Client", return_value=mock_client)

        paper = _make_paper("My Title", "My Abstract")
        summarize_papers([paper], SUMMARY_CONFIG)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs["contents"]
        assert "My Title" in prompt
        assert "Alice" in prompt
        assert "My Abstract" in prompt

    def test_raises_when_gemini_returns_empty_response(
        self, mocker: pytest.fixture
    ) -> None:
        mocker.patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
        mocker.patch("src.summarizer.time.sleep")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = ""
        mock_client.models.generate_content.return_value = mock_response
        mocker.patch("src.summarizer.genai.Client", return_value=mock_client)

        paper = _make_paper("Test Paper", "Test abstract")
        with pytest.raises(RuntimeError, match="Gemini API returned empty response"):
            summarize_papers([paper], SUMMARY_CONFIG)
