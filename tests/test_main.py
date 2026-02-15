from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from src.config import (
    AppConfig,
    NotificationConfig,
    SearchConfig,
    SummaryConfig,
)
from src.main import main
from src.models import Paper, SummarizedPaper


def _make_app_config() -> AppConfig:
    return AppConfig(
        search=SearchConfig(
            categories=["cs.AI"],
            keywords=["LLM"],
            max_results=5,
        ),
        summary=SummaryConfig(
            prompt_template="Title: {title}\nAbstract: {abstract}\nSummarize.",
        ),
        notification=NotificationConfig(
            slack_enabled=False,
            discord_enabled=False,
        ),
    )


def _make_paper() -> Paper:
    return Paper(
        arxiv_id="http://arxiv.org/abs/2501.00001v1",
        title="Test Paper",
        abstract="Test abstract",
        authors=["Alice"],
        published=datetime(2025, 1, 15, tzinfo=timezone.utc),
        url="http://arxiv.org/abs/2501.00001v1",
    )


class TestMain:
    def test_full_pipeline(self, mocker: pytest.fixture, tmp_path: pytest.fixture) -> None:
        config = _make_app_config()
        paper = _make_paper()
        summarized = SummarizedPaper(paper=paper, summary="要約テキスト")

        mocker.patch("src.main.load_dotenv")
        mock_load_config = mocker.patch("src.main.load_config", return_value=config)
        mock_collect = mocker.patch("src.main.collect_papers", return_value=[paper])
        mock_summarize = mocker.patch(
            "src.main.summarize_papers", return_value=[summarized]
        )
        mock_notify = mocker.patch("src.main.notify")

        config_path = str(tmp_path / "config.yaml")
        main(config_path)

        mock_load_config.assert_called_once_with(config_path)
        mock_collect.assert_called_once_with(config.search)
        mock_summarize.assert_called_once_with([paper], config.summary)
        mock_notify.assert_called_once_with(config.notification, [summarized])

    def test_skips_summarize_and_notify_when_no_papers(
        self, mocker: pytest.fixture, tmp_path: pytest.fixture
    ) -> None:
        config = _make_app_config()

        mocker.patch("src.main.load_dotenv")
        mocker.patch("src.main.load_config", return_value=config)
        mocker.patch("src.main.collect_papers", return_value=[])
        mock_summarize = mocker.patch("src.main.summarize_papers")
        mock_notify = mocker.patch("src.main.notify")

        config_path = str(tmp_path / "config.yaml")
        main(config_path)

        mock_summarize.assert_not_called()
        mock_notify.assert_not_called()
