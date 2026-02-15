"""Main entry point for arxiv agent."""
import logging
import sys
from arxiv_agent.config.loader import load_config
from arxiv_agent.collection.arxiv_client import ArxivClient
from arxiv_agent.summarization.prompt_builder import PromptBuilder
from arxiv_agent.summarization.gemini_client import GeminiClient
from arxiv_agent.notification.notifier import Notifier
from arxiv_agent.utils.logger import setup_logger

logger = logging.getLogger(__name__)


def main() -> int:
    """
    Main application flow.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        setup_logger()
        logger.info("Starting arxiv agent")

        config_path = sys.argv[1] if len(sys.argv) > 1 else "config/default.yaml"
        logger.info(f"Loading config from: {config_path}")
        config = load_config(config_path)

        arxiv_client = ArxivClient(max_results=config.arxiv.max_results)
        papers = arxiv_client.search_papers(
            categories=config.arxiv.categories,
            keywords=config.arxiv.keywords,
        )

        if not papers:
            logger.warning("No papers found")
            return 0

        prompt_builder = PromptBuilder(config.gemini.prompt_template)
        gemini_client = GeminiClient(
            prompt_builder=prompt_builder,
            model_name=config.gemini.model,
            temperature=config.gemini.temperature,
            max_tokens=config.gemini.max_tokens,
        )

        summaries = []
        for paper in papers:
            try:
                summary = gemini_client.summarize(paper)
                summaries.append(summary)
            except Exception as e:
                logger.error(f"Failed to summarize paper {paper.arxiv_id}: {e}")

        if not summaries:
            logger.warning("No summaries generated")
            return 0

        notifier = Notifier(config.notification)
        notifier.send_all(summaries)

        logger.info(f"Successfully processed {len(summaries)} papers")
        return 0

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
