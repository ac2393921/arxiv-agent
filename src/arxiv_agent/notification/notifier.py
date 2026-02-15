"""Notification orchestrator."""
import logging
from typing import List
from arxiv_agent.summarization.models import Summary
from arxiv_agent.config.models import NotificationConfig
from .slack import SlackNotifier
from .discord import DiscordNotifier

logger = logging.getLogger(__name__)


class Notifier:
    """Orchestrates notifications to multiple channels."""

    def __init__(self, config: NotificationConfig):
        """
        Initialize notifier.

        Args:
            config: Notification configuration
        """
        self.config = config
        self.notifiers = []

        if config.slack.enabled:
            try:
                self.notifiers.append(('Slack', SlackNotifier()))
                logger.info("Slack notifier enabled")
            except ValueError as e:
                logger.warning(f"Slack notifier disabled: {e}")

        if config.discord.enabled:
            try:
                self.notifiers.append(('Discord', DiscordNotifier()))
                logger.info("Discord notifier enabled")
            except ValueError as e:
                logger.warning(f"Discord notifier disabled: {e}")

    def send_all(self, summaries: List[Summary]) -> None:
        """
        Send summaries to all enabled notification channels.

        Args:
            summaries: List of summaries to send
        """
        if not summaries:
            logger.warning("No summaries to send")
            return

        if not self.notifiers:
            logger.warning("No notifiers enabled")
            return

        for name, notifier in self.notifiers:
            try:
                notifier.send(summaries)
            except Exception as e:
                logger.error(f"{name} notification failed: {e}")
