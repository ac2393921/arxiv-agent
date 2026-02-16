"""Tests for paper history management."""
import json
from pathlib import Path

import pytest

from arxiv_agent.history import PaperHistory


class TestPaperHistory:
    """Test cases for PaperHistory class."""

    def test_init_with_nonexistent_file(self, tmp_path: Path) -> None:
        """Test initialization with non-existent history file."""
        history_file = tmp_path / "history.json"
        history = PaperHistory(str(history_file))

        assert not history.is_processed("2301.12345v1")

    def test_init_with_existing_file(self, tmp_path: Path) -> None:
        """Test initialization with existing history file."""
        history_file = tmp_path / "history.json"
        history_file.write_text(
            json.dumps({"processed_papers": ["2301.12345v1", "2301.67890v2"]}),
            encoding="utf-8",
        )

        history = PaperHistory(str(history_file))

        assert history.is_processed("2301.12345v1")
        assert history.is_processed("2301.67890v2")
        assert not history.is_processed("2301.99999v1")

    def test_init_with_corrupted_file(self, tmp_path: Path) -> None:
        """Test initialization with corrupted JSON file."""
        history_file = tmp_path / "history.json"
        history_file.write_text("{ invalid json", encoding="utf-8")

        history = PaperHistory(str(history_file))

        assert not history.is_processed("2301.12345v1")

    def test_init_with_invalid_format(self, tmp_path: Path) -> None:
        """Test initialization with invalid data format."""
        history_file = tmp_path / "history.json"
        history_file.write_text(
            json.dumps({"processed_papers": "not_a_list"}),
            encoding="utf-8",
        )

        history = PaperHistory(str(history_file))

        assert not history.is_processed("2301.12345v1")

    def test_init_with_missing_key(self, tmp_path: Path) -> None:
        """Test initialization with missing 'processed_papers' key."""
        history_file = tmp_path / "history.json"
        history_file.write_text(json.dumps({"other_key": []}), encoding="utf-8")

        history = PaperHistory(str(history_file))

        assert not history.is_processed("2301.12345v1")

    def test_is_processed_returns_false_for_new_paper(self, tmp_path: Path) -> None:
        """Test is_processed returns False for new paper."""
        history_file = tmp_path / "history.json"
        history = PaperHistory(str(history_file))

        assert not history.is_processed("2301.12345v1")

    def test_is_processed_returns_true_for_existing_paper(self, tmp_path: Path) -> None:
        """Test is_processed returns True for existing paper."""
        history_file = tmp_path / "history.json"
        history_file.write_text(
            json.dumps({"processed_papers": ["2301.12345v1"]}),
            encoding="utf-8",
        )
        history = PaperHistory(str(history_file))

        assert history.is_processed("2301.12345v1")

    def test_mark_processed_saves_single_paper(self, tmp_path: Path) -> None:
        """Test marking a single paper as processed."""
        history_file = tmp_path / "history.json"
        history = PaperHistory(str(history_file))

        history.mark_processed(["2301.12345v1"])

        assert history.is_processed("2301.12345v1")
        assert history_file.exists()

        saved_data = json.loads(history_file.read_text(encoding="utf-8"))
        assert saved_data == {"processed_papers": ["2301.12345v1"]}

    def test_mark_processed_saves_multiple_papers(self, tmp_path: Path) -> None:
        """Test marking multiple papers as processed."""
        history_file = tmp_path / "history.json"
        history = PaperHistory(str(history_file))

        history.mark_processed(["2301.12345v1", "2301.67890v2"])

        assert history.is_processed("2301.12345v1")
        assert history.is_processed("2301.67890v2")

        saved_data = json.loads(history_file.read_text(encoding="utf-8"))
        assert set(saved_data["processed_papers"]) == {"2301.12345v1", "2301.67890v2"}

    def test_mark_processed_with_empty_list(self, tmp_path: Path) -> None:
        """Test marking empty list does not create file."""
        history_file = tmp_path / "history.json"
        history = PaperHistory(str(history_file))

        history.mark_processed([])

        assert not history_file.exists()

    def test_mark_processed_merges_with_existing(self, tmp_path: Path) -> None:
        """Test marking processed merges with existing history."""
        history_file = tmp_path / "history.json"
        history_file.write_text(
            json.dumps({"processed_papers": ["2301.12345v1"]}),
            encoding="utf-8",
        )
        history = PaperHistory(str(history_file))

        history.mark_processed(["2301.67890v2", "2301.99999v3"])

        assert history.is_processed("2301.12345v1")
        assert history.is_processed("2301.67890v2")
        assert history.is_processed("2301.99999v3")

        saved_data = json.loads(history_file.read_text(encoding="utf-8"))
        assert set(saved_data["processed_papers"]) == {
            "2301.12345v1",
            "2301.67890v2",
            "2301.99999v3",
        }

    def test_mark_processed_deduplicates_papers(self, tmp_path: Path) -> None:
        """Test marking same paper multiple times doesn't create duplicates."""
        history_file = tmp_path / "history.json"
        history = PaperHistory(str(history_file))

        history.mark_processed(["2301.12345v1"])
        history.mark_processed(["2301.12345v1", "2301.67890v2"])

        saved_data = json.loads(history_file.read_text(encoding="utf-8"))
        assert set(saved_data["processed_papers"]) == {"2301.12345v1", "2301.67890v2"}

    def test_persistence_across_instances(self, tmp_path: Path) -> None:
        """Test history persists across multiple instances."""
        history_file = tmp_path / "history.json"

        history1 = PaperHistory(str(history_file))
        history1.mark_processed(["2301.12345v1"])

        history2 = PaperHistory(str(history_file))
        assert history2.is_processed("2301.12345v1")

    def test_file_saved_in_sorted_order(self, tmp_path: Path) -> None:
        """Test saved file has papers in sorted order."""
        history_file = tmp_path / "history.json"
        history = PaperHistory(str(history_file))

        history.mark_processed(["2301.99999v1", "2301.12345v1", "2301.67890v2"])

        saved_data = json.loads(history_file.read_text(encoding="utf-8"))
        assert saved_data["processed_papers"] == [
            "2301.12345v1",
            "2301.67890v2",
            "2301.99999v1",
        ]

    def test_creates_parent_directory_if_missing(self, tmp_path: Path) -> None:
        """Test creates parent directory when saving."""
        history_file = tmp_path / "subdir" / "history.json"
        history = PaperHistory(str(history_file))

        history.mark_processed(["2301.12345v1"])

        assert history_file.exists()
        assert history_file.parent.is_dir()
