"""arXiv API client."""
import arxiv
import logging
from typing import List
from .models import Paper

logger = logging.getLogger(__name__)


class ArxivClient:
    """Client for fetching papers from arXiv API."""

    def __init__(self, max_results: int):
        """
        Initialize arXiv client.

        Args:
            max_results: Maximum number of papers to fetch
        """
        if max_results <= 0:
            raise ValueError("max_results must be positive")
        self.max_results = max_results

    def search_papers(self, categories: List[str], keywords: List[str]) -> List[Paper]:
        """
        Search papers matching categories and keywords.

        Args:
            categories: List of arXiv categories (e.g., ['cs.AI', 'cs.LG'])
            keywords: List of keywords to search for

        Returns:
            List of Paper objects

        Raises:
            ValueError: If categories or keywords are empty
        """
        if not categories:
            raise ValueError("categories must not be empty")
        if not keywords:
            raise ValueError("keywords must not be empty")

        query = self._build_query(categories, keywords)
        logger.info(f"Searching arXiv with query: {query}")

        search = arxiv.Search(
            query=query,
            max_results=self.max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        papers = []
        for result in search.results():
            paper = Paper(
                arxiv_id=result.entry_id.split('/')[-1],
                title=result.title,
                authors=[author.name for author in result.authors],
                abstract=result.summary,
                published=result.published,
                categories=result.categories,
                pdf_url=result.pdf_url,
            )
            papers.append(paper)

        logger.info(f"Found {len(papers)} papers")
        return papers

    def _build_query(self, categories: List[str], keywords: List[str]) -> str:
        """
        Build arXiv API query string.

        Args:
            categories: List of categories
            keywords: List of keywords

        Returns:
            Query string
        """
        category_query = " OR ".join([f"cat:{cat}" for cat in categories])
        keyword_query = " OR ".join([f'all:"{kw}"' for kw in keywords])
        return f"({category_query}) AND ({keyword_query})"
