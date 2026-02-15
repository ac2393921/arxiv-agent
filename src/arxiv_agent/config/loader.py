"""Configuration loader."""
import yaml
from pathlib import Path
from .models import (
    Config,
    ArxivConfig,
    GeminiConfig,
    NotificationConfig,
    NotificationTarget,
)


def load_config(config_path: str) -> Config:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        Config: Loaded configuration

    Raises:
        FileNotFoundError: If config file does not exist
        ValueError: If config structure is invalid
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("Config file must contain a YAML object")

    return Config(
        arxiv=_load_arxiv_config(data.get('arxiv', {})),
        gemini=_load_gemini_config(data.get('gemini', {})),
        notification=_load_notification_config(data.get('notification', {})),
    )


def _load_arxiv_config(data: dict) -> ArxivConfig:
    """Load arxiv configuration section."""
    if not isinstance(data, dict):
        raise ValueError("arxiv config must be an object")

    categories = data.get('categories')
    if not isinstance(categories, list) or not categories:
        raise ValueError("arxiv.categories must be a non-empty list")

    keywords = data.get('keywords')
    if not isinstance(keywords, list) or not keywords:
        raise ValueError("arxiv.keywords must be a non-empty list")

    max_results = data.get('max_results')
    if not isinstance(max_results, int) or max_results <= 0:
        raise ValueError("arxiv.max_results must be a positive integer")

    return ArxivConfig(
        categories=categories,
        keywords=keywords,
        max_results=max_results,
    )


def _load_gemini_config(data: dict) -> GeminiConfig:
    """Load Gemini configuration section."""
    if not isinstance(data, dict):
        raise ValueError("gemini config must be an object")

    prompt_template = data.get('prompt_template')
    if not isinstance(prompt_template, str) or not prompt_template.strip():
        raise ValueError("gemini.prompt_template must be a non-empty string")

    model = data.get('model')
    if not isinstance(model, str) or not model.strip():
        raise ValueError("gemini.model must be a non-empty string")

    temperature = data.get('temperature')
    if not isinstance(temperature, (int, float)) or not (0 <= temperature <= 2):
        raise ValueError("gemini.temperature must be a number between 0 and 2")

    max_tokens = data.get('max_tokens')
    if not isinstance(max_tokens, int) or max_tokens <= 0:
        raise ValueError("gemini.max_tokens must be a positive integer")

    return GeminiConfig(
        prompt_template=prompt_template,
        model=model,
        temperature=float(temperature),
        max_tokens=max_tokens,
    )


def _load_notification_config(data: dict) -> NotificationConfig:
    """Load notification configuration section."""
    if not isinstance(data, dict):
        raise ValueError("notification config must be an object")

    slack_data = data.get('slack', {})
    if not isinstance(slack_data, dict):
        raise ValueError("notification.slack must be an object")

    discord_data = data.get('discord', {})
    if not isinstance(discord_data, dict):
        raise ValueError("notification.discord must be an object")

    return NotificationConfig(
        slack=NotificationTarget(enabled=bool(slack_data.get('enabled', False))),
        discord=NotificationTarget(enabled=bool(discord_data.get('enabled', False))),
    )
