"""Tests for BaseWebhookNotifier."""
import pytest
from unittest.mock import Mock, patch
from arxiv_agent.notification.base_webhook_notifier import BaseWebhookNotifier
from arxiv_agent.summarization.models import Summary


class ConcreteWebhookNotifier(BaseWebhookNotifier):
    """Concrete implementation for testing."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.service_name = "Test"

    def _build_payload(self, message: str) -> dict:
        return {"text": message}

    def _format_bold(self, text: str) -> str:
        return f"**{text}**"


class TestBaseWebhookNotifier:
    """Test cases for BaseWebhookNotifier."""

    @patch('arxiv_agent.notification.base_webhook_notifier.requests.post')
    def test_send_successful_request(self, mock_post):
        """Should send HTTP POST request with correct parameters."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        notifier = ConcreteWebhookNotifier("http://test.webhook")
        summaries = [
            Summary(paper_id="1", title="Test", summary_text="Summary")
        ]

        notifier.send(summaries)

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['json'] == {"text": "📚 **論文要約 (1件)**\n\n**1. Test**\nID: 1\nSummary\n"}
        assert call_args[1]['timeout'] == 10
        assert call_args[0][0] == "http://test.webhook"
        mock_response.raise_for_status.assert_called_once()

    def test_send_with_empty_summaries(self):
        """Should return early and log warning when summaries list is empty."""
        notifier = ConcreteWebhookNotifier("http://test.webhook")

        # Should not raise, just return early
        notifier.send([])

    @patch('arxiv_agent.notification.base_webhook_notifier.requests.post')
    def test_send_raises_on_request_exception(self, mock_post):
        """Should log error and re-raise RequestException."""
        import requests
        mock_post.side_effect = requests.RequestException("Connection error")

        notifier = ConcreteWebhookNotifier("http://test.webhook")
        summaries = [
            Summary(paper_id="1", title="Test", summary_text="Summary")
        ]

        with pytest.raises(requests.RequestException, match="Connection error"):
            notifier.send(summaries)

    @patch('arxiv_agent.notification.base_webhook_notifier.requests.post')
    def test_send_timeout_parameter(self, mock_post):
        """Should set timeout to 10 seconds."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        notifier = ConcreteWebhookNotifier("http://test.webhook")
        summaries = [
            Summary(paper_id="1", title="Test", summary_text="Summary")
        ]

        notifier.send(summaries)

        # Verify timeout parameter
        assert mock_post.call_args[1]['timeout'] == 10
