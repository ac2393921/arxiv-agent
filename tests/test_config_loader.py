"""Tests for configuration loader."""
import pytest
import tempfile
from pathlib import Path
from arxiv_agent.config.loader import load_config
from arxiv_agent.config.models import Config


class TestConfigLoader:
    """Test cases for configuration loader."""

    def test_load_config_file_not_found(self):
        """Should raise FileNotFoundError when config file does not exist."""
        with pytest.raises(FileNotFoundError, match="Config file not found"):
            load_config("/nonexistent/path/config.yaml")

    def test_load_config_with_valid_yaml(self, tmp_path):
        """Should load valid configuration successfully."""
        config_content = """
arxiv:
  categories:
    - cs.AI
    - cs.LG
  keywords:
    - LLM
    - GPT
  max_results: 10

gemini:
  model: gemini-pro
  temperature: 0.7
  max_tokens: 1000
  prompt_template: "Summarize: {title} by {authors}. {abstract}"

notification:
  slack:
    enabled: true
  discord:
    enabled: false
"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(config_content)

        config = load_config(str(config_file))

        assert isinstance(config, Config)
        assert config.arxiv.categories == ["cs.AI", "cs.LG"]
        assert config.arxiv.keywords == ["LLM", "GPT"]
        assert config.arxiv.max_results == 10
        assert config.gemini.model == "gemini-pro"
        assert config.gemini.temperature == 0.7
        assert config.gemini.max_tokens == 1000
        assert config.notification.slack.enabled is True
        assert config.notification.discord.enabled is False

    def test_load_config_with_invalid_yaml(self, tmp_path):
        """Should raise ValueError when YAML is not an object."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("just a string")

        with pytest.raises(ValueError, match="Config file must contain a YAML object"):
            load_config(str(config_file))

    def test_load_config_missing_arxiv_categories(self, tmp_path):
        """Should raise ValueError when arxiv.categories is missing."""
        config_content = """
arxiv:
  keywords:
    - LLM
  max_results: 10
gemini:
  model: gemini-pro
  temperature: 0.7
  max_tokens: 1000
  prompt_template: "{title} {authors} {abstract}"
notification:
  slack:
    enabled: false
  discord:
    enabled: false
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(ValueError, match="arxiv.categories must be a non-empty list"):
            load_config(str(config_file))

    def test_load_config_empty_arxiv_categories(self, tmp_path):
        """Should raise ValueError when arxiv.categories is empty."""
        config_content = """
arxiv:
  categories: []
  keywords:
    - LLM
  max_results: 10
gemini:
  model: gemini-pro
  temperature: 0.7
  max_tokens: 1000
  prompt_template: "{title} {authors} {abstract}"
notification:
  slack:
    enabled: false
  discord:
    enabled: false
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(ValueError, match="arxiv.categories must be a non-empty list"):
            load_config(str(config_file))

    def test_load_config_invalid_max_results(self, tmp_path):
        """Should raise ValueError when max_results is not positive."""
        config_content = """
arxiv:
  categories:
    - cs.AI
  keywords:
    - LLM
  max_results: 0
gemini:
  model: gemini-pro
  temperature: 0.7
  max_tokens: 1000
  prompt_template: "{title} {authors} {abstract}"
notification:
  slack:
    enabled: false
  discord:
    enabled: false
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(ValueError, match="arxiv.max_results must be a positive integer"):
            load_config(str(config_file))

    def test_load_config_invalid_temperature(self, tmp_path):
        """Should raise ValueError when temperature is out of range."""
        config_content = """
arxiv:
  categories:
    - cs.AI
  keywords:
    - LLM
  max_results: 10
gemini:
  model: gemini-pro
  temperature: 3.0
  max_tokens: 1000
  prompt_template: "{title} {authors} {abstract}"
notification:
  slack:
    enabled: false
  discord:
    enabled: false
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(ValueError, match="gemini.temperature must be a number between 0 and 2"):
            load_config(str(config_file))

    def test_load_config_empty_prompt_template(self, tmp_path):
        """Should raise ValueError when prompt_template is empty."""
        config_content = """
arxiv:
  categories:
    - cs.AI
  keywords:
    - LLM
  max_results: 10
gemini:
  model: gemini-pro
  temperature: 0.7
  max_tokens: 1000
  prompt_template: ""
notification:
  slack:
    enabled: false
  discord:
    enabled: false
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(ValueError, match="gemini.prompt_template must be a non-empty string"):
            load_config(str(config_file))

    def test_load_default_config(self):
        """Should successfully load the default configuration file."""
        default_config_path = Path(__file__).parent.parent / "config" / "default.yaml"

        config = load_config(str(default_config_path))

        assert isinstance(config, Config)
        assert "cs.AI" in config.arxiv.categories
        assert "cs.LG" in config.arxiv.categories
        assert "cs.CL" in config.arxiv.categories
        assert "cs.SE" in config.arxiv.categories
        assert len(config.arxiv.categories) == 4

        assert "LLM" in config.arxiv.keywords
        assert "Software Architecture" in config.arxiv.keywords
        assert "Clean Code" in config.arxiv.keywords
        assert "Test-Driven Development" in config.arxiv.keywords
        assert len(config.arxiv.keywords) == 26

        assert config.arxiv.max_results == 10
