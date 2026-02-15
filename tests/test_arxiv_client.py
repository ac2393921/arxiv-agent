"""Tests for arxiv client."""
import pytest
from datetime import datetime
from arxiv_agent.collection.arxiv_client import ArxivClient


class TestArxivClient:
    """Test cases for ArxivClient."""

    def test_init_with_positive_max_results(self):
        """Should initialize successfully with positive max_results."""
        client = ArxivClient(max_results=10)
        assert client.max_results == 10

    def test_init_with_zero_max_results(self):
        """Should raise ValueError when max_results is zero."""
        with pytest.raises(ValueError, match="max_results must be positive"):
            ArxivClient(max_results=0)

    def test_init_with_negative_max_results(self):
        """Should raise ValueError when max_results is negative."""
        with pytest.raises(ValueError, match="max_results must be positive"):
            ArxivClient(max_results=-1)

    def test_build_query_with_single_category_and_keyword(self):
        """Should build query correctly with single category and keyword."""
        client = ArxivClient(max_results=10)
        query = client._build_query(['cs.AI'], ['LLM'])
        assert query == '(cat:cs.AI) AND (all:"LLM")'

    def test_build_query_with_multiple_categories_and_keywords(self):
        """Should build query with OR logic for multiple items."""
        client = ArxivClient(max_results=10)
        query = client._build_query(['cs.AI', 'cs.LG'], ['LLM', 'GPT'])
        assert query == '(cat:cs.AI OR cat:cs.LG) AND (all:"LLM" OR all:"GPT")'

    def test_search_papers_with_empty_categories(self):
        """Should raise ValueError when categories is empty."""
        client = ArxivClient(max_results=10)
        with pytest.raises(ValueError, match="categories must not be empty"):
            client.search_papers([], ['LLM'])

    def test_search_papers_with_empty_keywords(self):
        """Should raise ValueError when keywords is empty."""
        client = ArxivClient(max_results=10)
        with pytest.raises(ValueError, match="keywords must not be empty"):
            client.search_papers(['cs.AI'], [])
