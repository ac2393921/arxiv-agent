import arxiv

from src.config import SearchConfig
from src.models import Paper


def _build_query(config: SearchConfig) -> str:
    category_parts = [f"cat:{cat}" for cat in config.categories]
    category_query = " OR ".join(category_parts)

    keyword_parts = [f"(ti:{kw} OR abs:{kw})" for kw in config.keywords]
    keyword_query = " OR ".join(keyword_parts)

    return f"({category_query}) AND ({keyword_query})"


def collect_papers(config: SearchConfig) -> list[Paper]:
    query = _build_query(config)

    search = arxiv.Search(
        query=query,
        max_results=config.max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    client = arxiv.Client()
    results = client.results(search)

    papers: list[Paper] = []
    for result in results:
        paper = Paper(
            arxiv_id=result.entry_id,
            title=result.title,
            abstract=result.summary,
            authors=[author.name for author in result.authors],
            published=result.published,
            url=result.entry_id,
        )
        papers.append(paper)

    return papers
