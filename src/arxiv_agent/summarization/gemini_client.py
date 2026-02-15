"""Gemini API client for summarization."""
import os
import logging
from google import genai
from google.genai import types
from arxiv_agent.collection.models import Paper
from .models import Summary
from .prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for generating summaries using Gemini API."""

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        model_name: str,
        temperature: float,
        max_tokens: int,
    ):
        """
        Initialize Gemini client.

        Args:
            prompt_builder: Prompt builder instance
            model_name: Gemini model name
            temperature: Generation temperature (0-2)
            max_tokens: Maximum tokens to generate

        Raises:
            ValueError: If GEMINI_API_KEY environment variable is not set
        """
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        if not (0 <= temperature <= 2):
            raise ValueError("temperature must be between 0 and 2")

        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        self.client = genai.Client(api_key=api_key)
        self.prompt_builder = prompt_builder
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def summarize(self, paper: Paper) -> Summary:
        """
        Generate summary for a paper.

        Args:
            paper: Paper to summarize

        Returns:
            Summary object

        Raises:
            Exception: If API call fails
        """
        prompt = self.prompt_builder.build(paper)
        logger.info(f"Generating summary for paper: {paper.arxiv_id}")

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                ),
            )

            summary_text = response.text
            logger.info(f"Summary generated for {paper.arxiv_id}")

            return Summary(
                paper_id=paper.arxiv_id,
                title=paper.title,
                summary_text=summary_text,
            )

        except Exception as e:
            logger.error(f"Failed to generate summary for {paper.arxiv_id}: {e}")
            raise
