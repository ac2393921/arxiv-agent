"""Tests for Discord notifier."""
import pytest
from unittest.mock import patch
from arxiv_agent.notification.discord import DiscordNotifier
from arxiv_agent.summarization.models import Summary


class TestDiscordNotifier:
    """Test cases for DiscordNotifier."""

    def test_init_without_webhook_url(self):
        """Should raise ValueError when DISCORD_WEBHOOK_URL is not set."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="DISCORD_WEBHOOK_URL environment variable is required"):
                DiscordNotifier()

    def test_init_with_webhook_url(self):
        """Should initialize successfully with webhook URL."""
        with patch.dict('os.environ', {'DISCORD_WEBHOOK_URL': 'http://discord.test'}):
            notifier = DiscordNotifier()
            assert notifier.webhook_url == 'http://discord.test'

    def test_format_message_with_single_summary(self):
        """Should format single summary correctly."""
        with patch.dict('os.environ', {'DISCORD_WEBHOOK_URL': 'http://discord.test'}):
            notifier = DiscordNotifier()
            summaries = [
                Summary(
                    paper_id="2024.12345",
                    title="Test Paper",
                    summary_text="This is a test summary.",
                )
            ]

            message = notifier._format_message(summaries)

            assert "📚 **論文要約 (1件)**" in message
            assert "**1. Test Paper**" in message
            assert "ID: 2024.12345" in message
            assert "This is a test summary." in message

    def test_format_message_with_multiple_summaries(self):
        """Should format multiple summaries correctly."""
        with patch.dict('os.environ', {'DISCORD_WEBHOOK_URL': 'http://discord.test'}):
            notifier = DiscordNotifier()
            summaries = [
                Summary(
                    paper_id="2024.001",
                    title="First Paper",
                    summary_text="First summary.",
                ),
                Summary(
                    paper_id="2024.002",
                    title="Second Paper",
                    summary_text="Second summary.",
                ),
            ]

            message = notifier._format_message(summaries)

            assert "📚 **論文要約 (2件)**" in message
            assert "**1. First Paper**" in message
            assert "ID: 2024.001" in message
            assert "First summary." in message
            assert "**2. Second Paper**" in message
            assert "ID: 2024.002" in message
            assert "Second summary." in message
