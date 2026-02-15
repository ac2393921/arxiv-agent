"""Configuration data models."""
from dataclasses import dataclass
from typing import List


@dataclass
class ArxivConfig:
    """arxiv API search configuration."""
    categories: List[str]
    keywords: List[str]
    max_results: int


@dataclass
class GeminiConfig:
    """Gemini API configuration."""
    prompt_template: str
    model: str
    temperature: float
    max_tokens: int


@dataclass
class NotificationTarget:
    """Notification target configuration."""
    enabled: bool


@dataclass
class NotificationConfig:
    """Notification configuration."""
    slack: NotificationTarget
    discord: NotificationTarget


@dataclass
class Config:
    """Application configuration."""
    arxiv: ArxivConfig
    gemini: GeminiConfig
    notification: NotificationConfig
