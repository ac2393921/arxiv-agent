"""Tests for notification orchestrator."""
import pytest
from unittest.mock import Mock, patch
from arxiv_agent.notification.notifier import Notifier
from arxiv_agent.config.models import NotificationConfig, NotificationTarget
from arxiv_agent.summarization.models import Summary


class TestNotifier:
    """Test cases for Notifier."""

    def test_init_with_slack_enabled(self):
        """Should initialize Slack notifier when enabled."""
        config = NotificationConfig(
            slack=NotificationTarget(enabled=True),
            discord=NotificationTarget(enabled=False),
        )

        with patch.dict('os.environ', {'SLACK_WEBHOOK_URL': 'http://slack.test'}):
            notifier = Notifier(config)
            assert len(notifier.notifiers) == 1
            assert notifier.notifiers[0][0] == 'Slack'

    def test_init_with_discord_enabled(self):
        """Should initialize Discord notifier when enabled."""
        config = NotificationConfig(
            slack=NotificationTarget(enabled=False),
            discord=NotificationTarget(enabled=True),
        )

        with patch.dict('os.environ', {'DISCORD_WEBHOOK_URL': 'http://discord.test'}):
            notifier = Notifier(config)
            assert len(notifier.notifiers) == 1
            assert notifier.notifiers[0][0] == 'Discord'

    def test_init_with_both_enabled(self):
        """Should initialize both notifiers when both enabled."""
        config = NotificationConfig(
            slack=NotificationTarget(enabled=True),
            discord=NotificationTarget(enabled=True),
        )

        with patch.dict('os.environ', {
            'SLACK_WEBHOOK_URL': 'http://slack.test',
            'DISCORD_WEBHOOK_URL': 'http://discord.test'
        }):
            notifier = Notifier(config)
            assert len(notifier.notifiers) == 2

    def test_init_with_both_disabled(self):
        """Should initialize with no notifiers when both disabled."""
        config = NotificationConfig(
            slack=NotificationTarget(enabled=False),
            discord=NotificationTarget(enabled=False),
        )

        notifier = Notifier(config)
        assert len(notifier.notifiers) == 0

    def test_send_all_with_empty_summaries(self):
        """Should handle empty summaries list."""
        config = NotificationConfig(
            slack=NotificationTarget(enabled=True),
            discord=NotificationTarget(enabled=False),
        )

        with patch.dict('os.environ', {'SLACK_WEBHOOK_URL': 'http://slack.test'}):
            notifier = Notifier(config)
            notifier.send_all([])  # Should not raise

    def test_send_all_with_no_notifiers(self):
        """Should handle case with no enabled notifiers."""
        config = NotificationConfig(
            slack=NotificationTarget(enabled=False),
            discord=NotificationTarget(enabled=False),
        )

        notifier = Notifier(config)
        summaries = [
            Summary(paper_id="1", title="Test", summary_text="Summary")
        ]
        notifier.send_all(summaries)  # Should not raise

    def test_send_all_continues_on_error(self):
        """Should continue sending to other notifiers if one fails."""
        config = NotificationConfig(
            slack=NotificationTarget(enabled=True),
            discord=NotificationTarget(enabled=True),
        )

        mock_slack = Mock()
        mock_slack.send.side_effect = Exception("Slack error")
        mock_discord = Mock()

        with patch.dict('os.environ', {
            'SLACK_WEBHOOK_URL': 'http://slack.test',
            'DISCORD_WEBHOOK_URL': 'http://discord.test'
        }):
            notifier = Notifier(config)
            notifier.notifiers = [('Slack', mock_slack), ('Discord', mock_discord)]

            summaries = [
                Summary(paper_id="1", title="Test", summary_text="Summary")
            ]
            notifier.send_all(summaries)

            mock_slack.send.assert_called_once_with(summaries)
            mock_discord.send.assert_called_once_with(summaries)
