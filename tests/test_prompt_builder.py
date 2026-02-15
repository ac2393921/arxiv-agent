"""Tests for prompt builder."""
import pytest
from datetime import datetime
from arxiv_agent.summarization.prompt_builder import PromptBuilder
from arxiv_agent.collection.models import Paper


class TestPromptBuilder:
    """Test cases for PromptBuilder."""

    def test_init_with_valid_template(self):
        """Should initialize with template containing all placeholders."""
        template = "Title: {title}\nAuthors: {authors}\nAbstract: {abstract}"
        builder = PromptBuilder(template)
        assert builder.template == template

    def test_init_with_empty_template(self):
        """Should raise ValueError when template is empty."""
        with pytest.raises(ValueError, match="template must not be empty"):
            PromptBuilder("")

    def test_init_with_whitespace_only_template(self):
        """Should raise ValueError when template is whitespace only."""
        with pytest.raises(ValueError, match="template must not be empty"):
            PromptBuilder("   ")

    def test_init_without_title_placeholder(self):
        """Should raise ValueError when template missing {title}."""
        template = "Authors: {authors}\nAbstract: {abstract}"
        with pytest.raises(ValueError, match="must contain all placeholders"):
            PromptBuilder(template)

    def test_init_without_authors_placeholder(self):
        """Should raise ValueError when template missing {authors}."""
        template = "Title: {title}\nAbstract: {abstract}"
        with pytest.raises(ValueError, match="must contain all placeholders"):
            PromptBuilder(template)

    def test_init_without_abstract_placeholder(self):
        """Should raise ValueError when template missing {abstract}."""
        template = "Title: {title}\nAuthors: {authors}"
        with pytest.raises(ValueError, match="must contain all placeholders"):
            PromptBuilder(template)

    def test_build_with_single_author(self):
        """Should format prompt correctly with single author."""
        template = "Title: {title}\nAuthors: {authors}\nAbstract: {abstract}"
        builder = PromptBuilder(template)

        paper = Paper(
            arxiv_id="2101.00001",
            title="Test Paper",
            authors=["John Doe"],
            abstract="This is a test abstract.",
            published=datetime.now(),
            categories=["cs.AI"],
            pdf_url="http://example.com/paper.pdf",
        )

        result = builder.build(paper)
        expected = "Title: Test Paper\nAuthors: John Doe\nAbstract: This is a test abstract."
        assert result == expected

    def test_build_with_multiple_authors(self):
        """Should join multiple authors with comma."""
        template = "{title} by {authors}: {abstract}"
        builder = PromptBuilder(template)

        paper = Paper(
            arxiv_id="2101.00001",
            title="Test Paper",
            authors=["John Doe", "Jane Smith", "Bob Johnson"],
            abstract="Abstract text.",
            published=datetime.now(),
            categories=["cs.AI"],
            pdf_url="http://example.com/paper.pdf",
        )

        result = builder.build(paper)
        expected = "Test Paper by John Doe, Jane Smith, Bob Johnson: Abstract text."
        assert result == expected
