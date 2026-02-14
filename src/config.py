from dataclasses import dataclass

import yaml


@dataclass(frozen=True)
class SearchConfig:
    categories: list[str]
    keywords: list[str]
    max_results: int

    def __post_init__(self) -> None:
        if not self.categories:
            raise ValueError("categories is required")
        if not self.keywords:
            raise ValueError("keywords is required")
        if self.max_results <= 0:
            raise ValueError("max_results must be positive")


@dataclass(frozen=True)
class SummaryConfig:
    prompt_template: str

    def __post_init__(self) -> None:
        if not self.prompt_template:
            raise ValueError("prompt_template is required")
        if "{title}" not in self.prompt_template:
            raise ValueError("prompt_template must contain {title}")
        if "{abstract}" not in self.prompt_template:
            raise ValueError("prompt_template must contain {abstract}")


@dataclass(frozen=True)
class NotificationConfig:
    slack_enabled: bool
    discord_enabled: bool


@dataclass(frozen=True)
class AppConfig:
    search: SearchConfig
    summary: SummaryConfig
    notification: NotificationConfig


def load_config(path: str) -> AppConfig:
    with open(path) as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError("config file must be a YAML mapping")

    search_raw = raw.get("search")
    if not isinstance(search_raw, dict):
        raise ValueError("'search' section is required")

    summary_raw = raw.get("summary")
    if not isinstance(summary_raw, dict):
        raise ValueError("'summary' section is required")

    notification_raw = raw.get("notification")
    if not isinstance(notification_raw, dict):
        raise ValueError("'notification' section is required")

    search = SearchConfig(
        categories=search_raw["categories"],
        keywords=search_raw["keywords"],
        max_results=search_raw["max_results"],
    )

    summary = SummaryConfig(
        prompt_template=summary_raw["prompt_template"],
    )

    notification = NotificationConfig(
        slack_enabled=notification_raw["slack_enabled"],
        discord_enabled=notification_raw["discord_enabled"],
    )

    return AppConfig(
        search=search,
        summary=summary,
        notification=notification,
    )
