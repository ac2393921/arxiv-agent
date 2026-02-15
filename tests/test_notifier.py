import os
from datetime import datetime, timezone

import pytest
import responses

from src.config import NotificationConfig
from src.models import Paper, SummarizedPaper
from src.notifier import notify

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/test"


def _make_summarized_paper(title: str, summary: str) -> SummarizedPaper:
    paper = Paper(
        arxiv_id="http://arxiv.org/abs/2501.00001v1",
        title=title,
        abstract="abstract",
        authors=["Alice"],
        published=datetime(2025, 1, 15, tzinfo=timezone.utc),
        url="http://arxiv.org/abs/2501.00001v1",
    )
    return SummarizedPaper(paper=paper, summary=summary)


class TestNotify:
    @responses.activate
    def test_sends_to_slack_when_enabled(self, mocker: pytest.fixture) -> None:
        mocker.patch.dict(
            os.environ, {"SLACK_WEBHOOK_URL": "https://hooks.slack.com/test"}
        )
        responses.add(
            responses.POST, "https://hooks.slack.com/test", status=200
        )

        config = NotificationConfig(slack_enabled=True, discord_enabled=False)
        papers = [_make_summarized_paper("Test Paper", "Test summary")]
        notify(config, papers)

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == "https://hooks.slack.com/test"

    @responses.activate
    def test_sends_to_discord_when_enabled(self, mocker: pytest.fixture) -> None:
        mocker.patch.dict(
            os.environ, {"DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/test"}
        )
        responses.add(
            responses.POST, "https://discord.com/api/webhooks/test", status=200
        )

        config = NotificationConfig(slack_enabled=False, discord_enabled=True)
        papers = [_make_summarized_paper("Test Paper", "Test summary")]
        notify(config, papers)

        assert len(responses.calls) == 1

    def test_does_nothing_when_no_papers(self) -> None:
        config = NotificationConfig(slack_enabled=True, discord_enabled=True)
        notify(config, [])

    def test_does_nothing_when_both_disabled(self) -> None:
        config = NotificationConfig(slack_enabled=False, discord_enabled=False)
        papers = [_make_summarized_paper("Test Paper", "Test summary")]
        notify(config, papers)

    def test_raises_when_slack_url_missing(self, mocker: pytest.fixture) -> None:
        mocker.patch.dict(os.environ, {}, clear=True)
        config = NotificationConfig(slack_enabled=True, discord_enabled=False)
        papers = [_make_summarized_paper("Test Paper", "Test summary")]

        with pytest.raises(
            RuntimeError, match="SLACK_WEBHOOK_URL environment variable is not set"
        ):
            notify(config, papers)

    def test_raises_when_discord_url_missing(self, mocker: pytest.fixture) -> None:
        mocker.patch.dict(os.environ, {}, clear=True)
        config = NotificationConfig(slack_enabled=False, discord_enabled=True)
        papers = [_make_summarized_paper("Test Paper", "Test summary")]

        with pytest.raises(
            RuntimeError, match="DISCORD_WEBHOOK_URL environment variable is not set"
        ):
            notify(config, papers)

    @responses.activate
    def test_sends_to_both_when_both_enabled(self, mocker: pytest.fixture) -> None:
        mocker.patch.dict(
            os.environ,
            {
                "SLACK_WEBHOOK_URL": "https://hooks.slack.com/test",
                "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/test",
            },
        )
        responses.add(responses.POST, "https://hooks.slack.com/test", status=200)
        responses.add(
            responses.POST, "https://discord.com/api/webhooks/test", status=200
        )

        config = NotificationConfig(slack_enabled=True, discord_enabled=True)
        papers = [_make_summarized_paper("Test Paper", "Test summary")]
        notify(config, papers)

        assert len(responses.calls) == 2

    @responses.activate
    def test_discord_sends_single_message_for_short_content(
        self, mocker: pytest.fixture
    ) -> None:
        mocker.patch.dict(os.environ, {"DISCORD_WEBHOOK_URL": DISCORD_WEBHOOK_URL})
        responses.add(responses.POST, DISCORD_WEBHOOK_URL, status=200)

        config = NotificationConfig(slack_enabled=False, discord_enabled=True)
        papers = [_make_summarized_paper("Short Title", "Short summary")]
        notify(config, papers)

        assert len(responses.calls) == 1
        body = responses.calls[0].request.body
        assert body is not None

    @responses.activate
    def test_discord_splits_long_content_into_multiple_messages(
        self, mocker: pytest.fixture
    ) -> None:
        mocker.patch.dict(os.environ, {"DISCORD_WEBHOOK_URL": DISCORD_WEBHOOK_URL})
        responses.add(responses.POST, DISCORD_WEBHOOK_URL, status=200)

        long_summary = "x" * 1500
        config = NotificationConfig(slack_enabled=False, discord_enabled=True)
        papers = [
            _make_summarized_paper(f"Paper {i}", long_summary) for i in range(3)
        ]
        notify(config, papers)

        assert len(responses.calls) > 1
