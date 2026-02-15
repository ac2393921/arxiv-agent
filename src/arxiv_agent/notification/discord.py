"""Discord notification adapter."""
from .base_webhook_notifier import BaseWebhookNotifier


class DiscordNotifier(BaseWebhookNotifier):
    """Discord webhook notifier."""

    def __init__(self):
        """
        Initialize Discord notifier.

        Raises:
            ValueError: If DISCORD_WEBHOOK_URL environment variable is not set
        """
        super().__init__('DISCORD_WEBHOOK_URL', 'Discord')

    def _build_payload(self, message: str) -> dict:
        """
        Build Discord webhook payload.

        Args:
            message: Formatted message string

        Returns:
            Payload dictionary for Discord webhook
        """
        return {"content": message}

    def _format_bold(self, text: str) -> str:
        """
        Format text as bold for Discord.

        Args:
            text: Text to format

        Returns:
            Bold-formatted text
        """
        return f"**{text}**"
