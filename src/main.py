import logging
import sys

from dotenv import load_dotenv

from src.collector import collect_papers
from src.config import load_config
from src.notifier import notify
from src.summarizer import summarize_papers

logger = logging.getLogger(__name__)


def main(config_path: str) -> None:
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logger.info("Loading configuration from %s", config_path)
    config = load_config(config_path)

    logger.info("Collecting papers from arXiv")
    papers = collect_papers(config.search)
    logger.info("Collected %d papers", len(papers))

    if not papers:
        logger.info("No papers found, exiting")
        return

    logger.info("Summarizing papers with Gemini API")
    summarized = summarize_papers(papers, config.summary)
    logger.info("Summarized %d papers", len(summarized))

    logger.info("Sending notifications")
    notify(config.notification, summarized)
    logger.info("Done")


if __name__ == "__main__":
    try:
        config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
        main(config_path)
    except Exception:
        logger.exception("Fatal error in main")
        sys.exit(1)
