"""Base webhook notifier for common webhook logic."""
import os
import requests
import logging
from typing import List
from abc import ABC, abstractmethod
from arxiv_agent.summarization.models import Summary

logger = logging.getLogger(__name__)


class BaseWebhookNotifier(ABC):
    """Base class for webhook-based notifiers."""

    def __init__(self, env_var_name: str, service_name: str):
        """
        Initialize webhook notifier.

        Args:
            env_var_name: Environment variable name for webhook URL
            service_name: Name of the service (e.g., "Slack", "Discord")

        Raises:
            ValueError: If webhook URL environment variable is not set
        """
        webhook_url = os.getenv(env_var_name)
        if not webhook_url:
            raise ValueError(f"{env_var_name} environment variable is required")

        self.webhook_url = webhook_url
        self.service_name = service_name

    def send(self, summaries: List[Summary]) -> None:
        """
        Send summaries to webhook.

        Args:
            summaries: List of summaries to send

        Raises:
            Exception: If webhook request fails
        """
        if not summaries:
            logger.warning(f"No summaries to send to {self.service_name}")
            return

        message = self._format_message(summaries)
        payload = self._build_payload(message)

        logger.info(f"Sending {len(summaries)} summaries to {self.service_name}")

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            logger.info(f"Summaries sent to {self.service_name} successfully")

        except requests.RequestException as e:
            logger.error(f"Failed to send to {self.service_name}: {e}")
            raise

    def _format_message(self, summaries: List[Summary]) -> str:
        """
        Format summaries into message.

        Args:
            summaries: List of summaries

        Returns:
            Formatted message string
        """
        lines = [f"📚 {self._format_bold(f'論文要約 ({len(summaries)}件)')}\n"]

        for i, summary in enumerate(summaries, 1):
            lines.append(self._format_bold(f"{i}. {summary.title}"))
            lines.append(f"ID: {summary.paper_id}")
            lines.append(summary.summary_text)
            lines.append("")

        return "\n".join(lines)

    @abstractmethod
    def _build_payload(self, message: str) -> dict:
        """
        Build webhook payload.

        Args:
            message: Formatted message string

        Returns:
            Payload dictionary for webhook
        """
        pass

    @abstractmethod
    def _format_bold(self, text: str) -> str:
        """
        Format text as bold.

        Args:
            text: Text to format

        Returns:
            Bold-formatted text
        """
        pass
