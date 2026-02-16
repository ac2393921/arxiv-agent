"""Integration tests for arxiv agent main flow."""
import json
from pathlib import Path
from datetime import datetime

import pytest

from arxiv_agent.collection.models import Paper
from arxiv_agent.summarization.models import Summary
from arxiv_agent.main import main


class TestArxivAgentMain:
    """Integration tests for main() function with history management."""

    def test_all_papers_are_new(
        self, tmp_path: pytest.fixture, mocker: pytest.fixture
    ) -> None:
        """Should process and save all papers when all are new."""
        # Setup
        config_file = tmp_path / "config.yaml"
        history_file = tmp_path / "history.json"
        config_file.write_text(
            f"""
arxiv:
  max_results: 10
  categories: ["cs.AI"]
  keywords: ["LLM"]
gemini:
  model: gemini-1.5-pro
  prompt_template: "Title: {{title}}, Authors: {{authors}}, Abstract: {{abstract}}"
  temperature: 0.7
  max_tokens: 1000
notification:
  slack:
    webhook_url: "https://hooks.slack.com/services/test"
history_file: "{history_file}"
""",
            encoding="utf-8",
        )

        papers = [
            Paper(
                arxiv_id="2301.00001v1",
                title="Paper 1",
                authors=["Author A"],
                abstract="Abstract 1",
                published=datetime(2023, 1, 1),
                categories=["cs.AI"],
                pdf_url="https://arxiv.org/pdf/2301.00001v1.pdf",
            ),
            Paper(
                arxiv_id="2301.00002v1",
                title="Paper 2",
                authors=["Author B"],
                abstract="Abstract 2",
                published=datetime(2023, 1, 2),
                categories=["cs.AI"],
                pdf_url="https://arxiv.org/pdf/2301.00002v1.pdf",
            ),
        ]
        summaries = [
            Summary(paper_id="2301.00001v1", title="Paper 1", summary_text="Summary 1"),
            Summary(paper_id="2301.00002v1", title="Paper 2", summary_text="Summary 2"),
        ]

        mocker.patch("sys.argv", ["main.py", str(config_file)])
        mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
        mocker.patch(
            "arxiv_agent.main.ArxivClient.search_papers", return_value=papers
        )
        mock_summarize = mocker.patch(
            "arxiv_agent.main.GeminiClient.summarize", side_effect=summaries
        )
        mocker.patch("arxiv_agent.main.Notifier.send_all")

        # Execute
        exit_code = main()

        # Verify
        assert exit_code == 0
        assert mock_summarize.call_count == 2

        history_data = json.loads(history_file.read_text(encoding="utf-8"))
        assert set(history_data["processed_papers"]) == {
            "2301.00001v1",
            "2301.00002v1",
        }

    def test_all_papers_are_processed(
        self, tmp_path: pytest.fixture, mocker: pytest.fixture
    ) -> None:
        """Should skip all papers when all are already processed."""
        # Setup
        config_file = tmp_path / "config.yaml"
        history_file = tmp_path / "history.json"
        config_file.write_text(
            f"""
arxiv:
  max_results: 10
  categories: ["cs.AI"]
  keywords: ["LLM"]
gemini:
  model: gemini-1.5-pro
  prompt_template: "Title: {{title}}, Authors: {{authors}}, Abstract: {{abstract}}"
  temperature: 0.7
  max_tokens: 1000
notification:
  slack:
    webhook_url: "https://hooks.slack.com/services/test"
history_file: "{history_file}"
""",
            encoding="utf-8",
        )
        history_file.write_text(
            json.dumps({"processed_papers": ["2301.00001v1", "2301.00002v1"]}),
            encoding="utf-8",
        )

        papers = [
            Paper(
                arxiv_id="2301.00001v1",
                title="Paper 1",
                authors=["Author A"],
                abstract="Abstract 1",
                published=datetime(2023, 1, 1),
                categories=["cs.AI"],
                pdf_url="https://arxiv.org/pdf/2301.00001v1.pdf",
            ),
            Paper(
                arxiv_id="2301.00002v1",
                title="Paper 2",
                authors=["Author B"],
                abstract="Abstract 2",
                published=datetime(2023, 1, 2),
                categories=["cs.AI"],
                pdf_url="https://arxiv.org/pdf/2301.00002v1.pdf",
            ),
        ]

        mocker.patch("sys.argv", ["main.py", str(config_file)])
        mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
        mocker.patch(
            "arxiv_agent.main.ArxivClient.search_papers", return_value=papers
        )
        mock_summarize = mocker.patch("arxiv_agent.main.GeminiClient.summarize")
        mocker.patch("arxiv_agent.main.Notifier.send_all")

        # Execute
        exit_code = main()

        # Verify
        assert exit_code == 0
        mock_summarize.assert_not_called()

        history_data = json.loads(history_file.read_text(encoding="utf-8"))
        assert set(history_data["processed_papers"]) == {
            "2301.00001v1",
            "2301.00002v1",
        }

    def test_mixed_new_and_processed_papers(
        self, tmp_path: pytest.fixture, mocker: pytest.fixture
    ) -> None:
        """Should process only new papers when mixed."""
        # Setup
        config_file = tmp_path / "config.yaml"
        history_file = tmp_path / "history.json"
        config_file.write_text(
            f"""
arxiv:
  max_results: 10
  categories: ["cs.AI"]
  keywords: ["LLM"]
gemini:
  model: gemini-1.5-pro
  prompt_template: "Title: {{title}}, Authors: {{authors}}, Abstract: {{abstract}}"
  temperature: 0.7
  max_tokens: 1000
notification:
  slack:
    webhook_url: "https://hooks.slack.com/services/test"
history_file: "{history_file}"
""",
            encoding="utf-8",
        )
        history_file.write_text(
            json.dumps({"processed_papers": ["2301.00001v1"]}),
            encoding="utf-8",
        )

        papers = [
            Paper(
                arxiv_id="2301.00001v1",
                title="Paper 1",
                authors=["Author A"],
                abstract="Abstract 1",
                published=datetime(2023, 1, 1),
                categories=["cs.AI"],
                pdf_url="https://arxiv.org/pdf/2301.00001v1.pdf",
            ),
            Paper(
                arxiv_id="2301.00002v1",
                title="Paper 2",
                authors=["Author B"],
                abstract="Abstract 2",
                published=datetime(2023, 1, 2),
                categories=["cs.AI"],
                pdf_url="https://arxiv.org/pdf/2301.00002v1.pdf",
            ),
        ]
        summaries = [
            Summary(paper_id="2301.00002v1", title="Paper 2", summary_text="Summary 2"),
        ]

        mocker.patch("sys.argv", ["main.py", str(config_file)])
        mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
        mocker.patch(
            "arxiv_agent.main.ArxivClient.search_papers", return_value=papers
        )
        mock_summarize = mocker.patch(
            "arxiv_agent.main.GeminiClient.summarize", side_effect=summaries
        )
        mocker.patch("arxiv_agent.main.Notifier.send_all")

        # Execute
        exit_code = main()

        # Verify
        assert exit_code == 0
        assert mock_summarize.call_count == 1

        history_data = json.loads(history_file.read_text(encoding="utf-8"))
        assert set(history_data["processed_papers"]) == {
            "2301.00001v1",
            "2301.00002v1",
        }

    def test_partial_summarization_failure(
        self, tmp_path: pytest.fixture, mocker: pytest.fixture
    ) -> None:
        """Should save only successfully summarized papers to history."""
        # Setup
        config_file = tmp_path / "config.yaml"
        history_file = tmp_path / "history.json"
        config_file.write_text(
            f"""
arxiv:
  max_results: 10
  categories: ["cs.AI"]
  keywords: ["LLM"]
gemini:
  model: gemini-1.5-pro
  prompt_template: "Title: {{title}}, Authors: {{authors}}, Abstract: {{abstract}}"
  temperature: 0.7
  max_tokens: 1000
notification:
  slack:
    webhook_url: "https://hooks.slack.com/services/test"
history_file: "{history_file}"
""",
            encoding="utf-8",
        )

        papers = [
            Paper(
                arxiv_id="2301.00001v1",
                title="Paper 1",
                authors=["Author A"],
                abstract="Abstract 1",
                published=datetime(2023, 1, 1),
                categories=["cs.AI"],
                pdf_url="https://arxiv.org/pdf/2301.00001v1.pdf",
            ),
            Paper(
                arxiv_id="2301.00002v1",
                title="Paper 2",
                authors=["Author B"],
                abstract="Abstract 2",
                published=datetime(2023, 1, 2),
                categories=["cs.AI"],
                pdf_url="https://arxiv.org/pdf/2301.00002v1.pdf",
            ),
            Paper(
                arxiv_id="2301.00003v1",
                title="Paper 3",
                authors=["Author C"],
                abstract="Abstract 3",
                published=datetime(2023, 1, 3),
                categories=["cs.AI"],
                pdf_url="https://arxiv.org/pdf/2301.00003v1.pdf",
            ),
        ]

        # Mock: Paper 1 succeeds, Paper 2 fails, Paper 3 succeeds
        def mock_summarize_side_effect(paper: Paper) -> Summary:
            if paper.arxiv_id == "2301.00002v1":
                raise Exception("API rate limit exceeded")
            return Summary(
                paper_id=paper.arxiv_id,
                title=paper.title,
                summary_text=f"Summary for {paper.title}",
            )

        mocker.patch("sys.argv", ["main.py", str(config_file)])
        mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
        mocker.patch(
            "arxiv_agent.main.ArxivClient.search_papers", return_value=papers
        )
        mock_summarize = mocker.patch(
            "arxiv_agent.main.GeminiClient.summarize",
            side_effect=mock_summarize_side_effect,
        )
        mocker.patch("arxiv_agent.main.Notifier.send_all")

        # Execute
        exit_code = main()

        # Verify
        assert exit_code == 0
        assert mock_summarize.call_count == 3

        # Only successfully summarized papers should be in history
        history_data = json.loads(history_file.read_text(encoding="utf-8"))
        assert set(history_data["processed_papers"]) == {
            "2301.00001v1",
            "2301.00003v1",
        }
        assert "2301.00002v1" not in history_data["processed_papers"]
