"""Tests for Gemini client."""
import pytest
from unittest.mock import patch
from arxiv_agent.summarization.gemini_client import GeminiClient
from arxiv_agent.summarization.prompt_builder import PromptBuilder


class TestGeminiClient:
    """Test cases for GeminiClient initialization."""

    def test_init_without_api_key(self):
        """Should raise ValueError when GEMINI_API_KEY is not set."""
        prompt_builder = PromptBuilder(template="Test: {title} by {authors}. {abstract}")

        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable is required"):
                GeminiClient(
                    prompt_builder=prompt_builder,
                    model_name="gemini-pro",
                    temperature=0.7,
                    max_tokens=1000,
                )

    def test_init_with_temperature_below_range(self):
        """Should raise ValueError when temperature is below 0."""
        prompt_builder = PromptBuilder(template="Test: {title} by {authors}. {abstract}")

        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            with pytest.raises(ValueError, match="temperature must be between 0 and 2"):
                GeminiClient(
                    prompt_builder=prompt_builder,
                    model_name="gemini-pro",
                    temperature=-1,
                    max_tokens=1000,
                )

    def test_init_with_temperature_above_range(self):
        """Should raise ValueError when temperature is above 2."""
        prompt_builder = PromptBuilder(template="Test: {title} by {authors}. {abstract}")

        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            with pytest.raises(ValueError, match="temperature must be between 0 and 2"):
                GeminiClient(
                    prompt_builder=prompt_builder,
                    model_name="gemini-pro",
                    temperature=3.0,
                    max_tokens=1000,
                )

    def test_init_with_zero_max_tokens(self):
        """Should raise ValueError when max_tokens is 0."""
        prompt_builder = PromptBuilder(template="Test: {title} by {authors}. {abstract}")

        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            with pytest.raises(ValueError, match="max_tokens must be positive"):
                GeminiClient(
                    prompt_builder=prompt_builder,
                    model_name="gemini-pro",
                    temperature=0.7,
                    max_tokens=0,
                )

    def test_init_with_negative_max_tokens(self):
        """Should raise ValueError when max_tokens is negative."""
        prompt_builder = PromptBuilder(template="Test: {title} by {authors}. {abstract}")

        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            with pytest.raises(ValueError, match="max_tokens must be positive"):
                GeminiClient(
                    prompt_builder=prompt_builder,
                    model_name="gemini-pro",
                    temperature=0.7,
                    max_tokens=-1,
                )

    def test_init_with_valid_parameters(self):
        """Should initialize successfully with valid parameters."""
        prompt_builder = PromptBuilder(template="Test: {title} by {authors}. {abstract}")

        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = GeminiClient(
                prompt_builder=prompt_builder,
                model_name="gemini-pro",
                temperature=0.7,
                max_tokens=1000,
            )

            assert client.prompt_builder == prompt_builder
            assert client.model_name == "gemini-pro"
            assert client.temperature == 0.7
            assert client.max_tokens == 1000
