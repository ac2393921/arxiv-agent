"""Paper history management for tracking processed papers."""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class PaperHistory:
    """
    Manages history of processed papers.

    Stores processed paper IDs in a JSON file to prevent duplicate processing.
    Handles file I/O errors gracefully to ensure application continues even if
    history management fails.
    """

    def __init__(self, history_file: str) -> None:
        """
        Initialize paper history manager.

        Args:
            history_file: Path to the JSON file storing processed paper IDs.
        """
        self._history_file = Path(history_file)
        self._processed_ids: set[str] = self._load_history()

    def _load_history(self) -> set[str]:
        """
        Load processed paper IDs from file.

        Returns:
            Set of processed paper IDs. Empty set if file doesn't exist or
            cannot be read.
        """
        if not self._history_file.exists():
            logger.info(f"History file not found: {self._history_file}. Starting with empty history.")
            return set()

        try:
            with self._history_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                processed_papers = data.get("processed_papers", [])
                if not isinstance(processed_papers, list):
                    logger.warning("Invalid history format: 'processed_papers' is not a list. Starting with empty history.")
                    return set()
                logger.info(f"Loaded {len(processed_papers)} processed paper IDs from history.")
                return set(processed_papers)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse history file: {e}. Starting with empty history.")
            return set()
        except OSError as e:
            logger.error(f"Failed to read history file: {e}. Starting with empty history.")
            return set()

    def is_processed(self, paper_id: str) -> bool:
        """
        Check if a paper has been processed.

        Args:
            paper_id: arXiv paper ID to check.

        Returns:
            True if paper has been processed, False otherwise.
        """
        return paper_id in self._processed_ids

    def mark_processed(self, paper_ids: list[str]) -> None:
        """
        Mark papers as processed and save to file.

        Args:
            paper_ids: List of arXiv paper IDs to mark as processed.
        """
        if not paper_ids:
            return

        self._processed_ids.update(paper_ids)
        self._save_history()

    def _save_history(self) -> None:
        """
        Save processed paper IDs to file.

        Logs error if save fails but does not raise exception to prevent
        disrupting main application flow.
        """
        try:
            self._history_file.parent.mkdir(parents=True, exist_ok=True)
            with self._history_file.open("w", encoding="utf-8") as f:
                data = {"processed_papers": sorted(self._processed_ids)}
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self._processed_ids)} processed paper IDs to history.")
        except OSError as e:
            logger.error(f"Failed to save history file: {e}")
