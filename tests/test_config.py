import os
import tempfile

import pytest

from src.config import (
    AppConfig,
    NotificationConfig,
    SearchConfig,
    SummaryConfig,
    load_config,
)


VALID_YAML = """\
search:
  categories:
    - "cs.AI"
  keywords:
    - "LLM"
  max_results: 10

summary:
  prompt_template: |
    タイトル: {title}
    著者: {authors}
    概要: {abstract}

notification:
  slack_enabled: false
  discord_enabled: true
"""


class TestSearchConfig:
    def test_valid_config(self) -> None:
        config = SearchConfig(
            categories=["cs.AI"],
            keywords=["LLM"],
            max_results=10,
        )
        assert config.categories == ["cs.AI"]
        assert config.keywords == ["LLM"]
        assert config.max_results == 10

    def test_empty_categories_raises(self) -> None:
        with pytest.raises(ValueError, match="categories is required"):
            SearchConfig(categories=[], keywords=["LLM"], max_results=10)

    def test_empty_keywords_raises(self) -> None:
        with pytest.raises(ValueError, match="keywords is required"):
            SearchConfig(categories=["cs.AI"], keywords=[], max_results=10)

    def test_zero_max_results_raises(self) -> None:
        with pytest.raises(ValueError, match="max_results must be positive"):
            SearchConfig(categories=["cs.AI"], keywords=["LLM"], max_results=0)

    def test_negative_max_results_raises(self) -> None:
        with pytest.raises(ValueError, match="max_results must be positive"):
            SearchConfig(categories=["cs.AI"], keywords=["LLM"], max_results=-1)


class TestSummaryConfig:
    def test_valid_config(self) -> None:
        config = SummaryConfig(
            prompt_template="Title: {title}\nAuthors: {authors}\nAbstract: {abstract}"
        )
        assert "{title}" in config.prompt_template

    def test_empty_template_raises(self) -> None:
        with pytest.raises(ValueError, match="prompt_template is required"):
            SummaryConfig(prompt_template="")

    def test_missing_title_placeholder_raises(self) -> None:
        with pytest.raises(ValueError, match="prompt_template must contain {title}"):
            SummaryConfig(prompt_template="Authors: {authors}\nAbstract: {abstract}")

    def test_missing_authors_placeholder_raises(self) -> None:
        with pytest.raises(ValueError, match="prompt_template must contain {authors}"):
            SummaryConfig(prompt_template="Title: {title}\nAbstract: {abstract}")

    def test_missing_abstract_placeholder_raises(self) -> None:
        with pytest.raises(
            ValueError, match="prompt_template must contain {abstract}"
        ):
            SummaryConfig(prompt_template="Title: {title}\nAuthors: {authors}")


class TestNotificationConfig:
    def test_valid_config(self) -> None:
        config = NotificationConfig(slack_enabled=True, discord_enabled=False)
        assert config.slack_enabled is True
        assert config.discord_enabled is False


class TestLoadConfig:
    def test_load_valid_config(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(VALID_YAML)
            f.flush()
            config = load_config(f.name)

        os.unlink(f.name)

        assert isinstance(config, AppConfig)
        assert config.search.categories == ["cs.AI"]
        assert config.search.keywords == ["LLM"]
        assert config.search.max_results == 10
        assert "{title}" in config.summary.prompt_template
        assert config.notification.slack_enabled is False
        assert config.notification.discord_enabled is True

    def test_missing_search_section_raises(self) -> None:
        yaml_content = """\
summary:
  prompt_template: "{title} {authors} {abstract}"
notification:
  slack_enabled: false
  discord_enabled: false
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(yaml_content)
            f.flush()

            with pytest.raises(ValueError, match="'search' section is required"):
                load_config(f.name)

        os.unlink(f.name)

    def test_missing_summary_section_raises(self) -> None:
        yaml_content = """\
search:
  categories: ["cs.AI"]
  keywords: ["LLM"]
  max_results: 10
notification:
  slack_enabled: false
  discord_enabled: false
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(yaml_content)
            f.flush()

            with pytest.raises(ValueError, match="'summary' section is required"):
                load_config(f.name)

        os.unlink(f.name)

    def test_missing_notification_section_raises(self) -> None:
        yaml_content = """\
search:
  categories: ["cs.AI"]
  keywords: ["LLM"]
  max_results: 10
summary:
  prompt_template: "{title} {authors} {abstract}"
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(yaml_content)
            f.flush()

            with pytest.raises(
                ValueError, match="'notification' section is required"
            ):
                load_config(f.name)

        os.unlink(f.name)

    def test_invalid_yaml_raises(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write("not a mapping")
            f.flush()

            with pytest.raises(ValueError, match="config file must be a YAML mapping"):
                load_config(f.name)

        os.unlink(f.name)

    def test_file_not_found_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path.yaml")
