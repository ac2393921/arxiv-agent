"""Prompt builder for summarization."""
from arxiv_agent.collection.models import Paper


class PromptBuilder:
    """Builder for summarization prompts."""

    def __init__(self, template: str):
        """
        Initialize prompt builder.

        Args:
            template: Prompt template with placeholders {title}, {authors}, {abstract}
        """
        if not template.strip():
            raise ValueError("template must not be empty")

        required_placeholders = {'{title}', '{authors}', '{abstract}'}
        if not all(ph in template for ph in required_placeholders):
            raise ValueError(f"template must contain all placeholders: {required_placeholders}")

        self.template = template

    def build(self, paper: Paper) -> str:
        """
        Build prompt for a paper.

        Args:
            paper: Paper to summarize

        Returns:
            Formatted prompt string
        """
        authors_str = ", ".join(paper.authors)
        return self.template.format(
            title=paper.title,
            authors=authors_str,
            abstract=paper.abstract,
        )
