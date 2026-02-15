"""Slack notification adapter."""
from .base_webhook_notifier import BaseWebhookNotifier


class SlackNotifier(BaseWebhookNotifier):
    """Slack webhook notifier."""

    def __init__(self):
        """
        Initialize Slack notifier.

        Raises:
            ValueError: If SLACK_WEBHOOK_URL environment variable is not set
        """
        super().__init__('SLACK_WEBHOOK_URL', 'Slack')

    def _build_payload(self, message: str) -> dict:
        """
        Build Slack webhook payload.

        Args:
            message: Formatted message string

        Returns:
            Payload dictionary for Slack webhook
        """
        return {"text": message}

    def _format_bold(self, text: str) -> str:
        """
        Format text as bold for Slack.

        Args:
            text: Text to format

        Returns:
            Bold-formatted text
        """
        return f"*{text}*"
