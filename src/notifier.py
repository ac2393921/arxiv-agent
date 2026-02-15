import logging
import os

import requests

from src.config import NotificationConfig
from src.models import SummarizedPaper

logger = logging.getLogger(__name__)

DISCORD_MESSAGE_LIMIT = 2000


def _format_paper_text(paper: SummarizedPaper) -> str:
    return (
        f"*{paper.paper.title}*\n"
        f"著者: {', '.join(paper.paper.authors)}\n"
        f"URL: {paper.paper.url}\n\n"
        f"{paper.summary}\n"
    )


def _send_slack(webhook_url: str, papers: list[SummarizedPaper]) -> None:
    header = ":newspaper: *本日のarXiv論文要約*\n\n"
    body_parts = [_format_paper_text(p) for p in papers]
    text = header + "\n---\n".join(body_parts)

    payload = {"text": text}
    response = requests.post(webhook_url, json=payload, timeout=30)
    response.raise_for_status()
    logger.info("Slack notification sent successfully")


def _split_discord_messages(papers: list[SummarizedPaper]) -> list[str]:
    header = "📰 **本日のarXiv論文要約**\n\n"
    separator = "\n---\n"

    messages: list[str] = []
    current = header

    for paper in papers:
        entry = _format_paper_text(paper)

        candidate = current + separator + entry if current != header else current + entry

        if len(candidate) > DISCORD_MESSAGE_LIMIT:
            if current != header:
                messages.append(current)
            current = entry
        else:
            current = candidate

    if current:
        messages.append(current)

    return messages


def _send_discord(webhook_url: str, papers: list[SummarizedPaper]) -> None:
    messages = _split_discord_messages(papers)

    for message in messages:
        payload = {"content": message}
        response = requests.post(webhook_url, json=payload, timeout=30)
        response.raise_for_status()

    logger.info("Discord notification sent successfully (%d messages)", len(messages))


def notify(config: NotificationConfig, papers: list[SummarizedPaper]) -> None:
    if not papers:
        logger.info("No papers to notify")
        return

    if config.slack_enabled:
        slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
        if not slack_webhook_url:
            raise RuntimeError("SLACK_WEBHOOK_URL environment variable is not set")
        _send_slack(slack_webhook_url, papers)

    if config.discord_enabled:
        discord_webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
        if not discord_webhook_url:
            raise RuntimeError("DISCORD_WEBHOOK_URL environment variable is not set")
        _send_discord(discord_webhook_url, papers)

    if not config.slack_enabled and not config.discord_enabled:
        logger.info("No notification channels enabled")
