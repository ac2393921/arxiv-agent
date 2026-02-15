"""Tests for main entry point."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from arxiv_agent.main import main


class TestMain:
    """Test cases for main() function."""

    @patch('arxiv_agent.main.load_config')
    @patch('arxiv_agent.main.ArxivClient')
    @patch('arxiv_agent.main.GeminiClient')
    @patch('arxiv_agent.main.Notifier')
    @patch('arxiv_agent.main.setup_logger')
    @patch('sys.argv', ['main.py', 'config/test.yaml'])
    def test_main_success_flow(self, mock_logger, mock_notifier_class,
                               mock_gemini_class, mock_arxiv_class, mock_load_config):
        """Should execute full workflow successfully and return 0."""
        mock_config = Mock()
        mock_config.arxiv.max_results = 10
        mock_config.arxiv.categories = ['cs.AI']
        mock_config.arxiv.keywords = ['LLM']
        mock_config.gemini.prompt_template = 'test template'
        mock_config.gemini.model = 'gemini-pro'
        mock_config.gemini.temperature = 0.7
        mock_config.gemini.max_tokens = 1000
        mock_config.notification = Mock()
        mock_load_config.return_value = mock_config

        mock_papers = [Mock(arxiv_id='1'), Mock(arxiv_id='2')]
        mock_arxiv = Mock()
        mock_arxiv.search_papers.return_value = mock_papers
        mock_arxiv_class.return_value = mock_arxiv

        mock_summaries = [Mock(), Mock()]
        mock_gemini = Mock()
        mock_gemini.summarize.side_effect = mock_summaries
        mock_gemini_class.return_value = mock_gemini

        mock_notifier = Mock()
        mock_notifier_class.return_value = mock_notifier

        result = main()

        assert result == 0
        mock_load_config.assert_called_once_with('config/test.yaml')
        mock_arxiv.search_papers.assert_called_once_with(
            categories=['cs.AI'],
            keywords=['LLM']
        )
        assert mock_gemini.summarize.call_count == 2
        mock_notifier.send_all.assert_called_once()

    @patch('arxiv_agent.main.load_config')
    @patch('arxiv_agent.main.ArxivClient')
    @patch('arxiv_agent.main.setup_logger')
    @patch('sys.argv', ['main.py', 'config/test.yaml'])
    def test_main_no_papers_found(self, mock_logger, mock_arxiv_class, mock_load_config):
        """Should return 0 when no papers found."""
        mock_config = Mock()
        mock_config.arxiv.max_results = 10
        mock_config.arxiv.categories = ['cs.AI']
        mock_config.arxiv.keywords = ['LLM']
        mock_load_config.return_value = mock_config

        mock_arxiv = Mock()
        mock_arxiv.search_papers.return_value = []
        mock_arxiv_class.return_value = mock_arxiv

        result = main()

        assert result == 0

    @patch('arxiv_agent.main.load_config')
    @patch('arxiv_agent.main.ArxivClient')
    @patch('arxiv_agent.main.GeminiClient')
    @patch('arxiv_agent.main.Notifier')
    @patch('arxiv_agent.main.setup_logger')
    @patch('sys.argv', ['main.py', 'config/test.yaml'])
    def test_main_partial_summarization_failure(self, mock_logger, mock_notifier_class,
                                                 mock_gemini_class, mock_arxiv_class, mock_load_config):
        """Should continue processing when some papers fail summarization."""
        mock_config = Mock()
        mock_config.arxiv.max_results = 10
        mock_config.arxiv.categories = ['cs.AI']
        mock_config.arxiv.keywords = ['LLM']
        mock_config.gemini.prompt_template = 'test template'
        mock_config.gemini.model = 'gemini-pro'
        mock_config.gemini.temperature = 0.7
        mock_config.gemini.max_tokens = 1000
        mock_config.notification = Mock()
        mock_load_config.return_value = mock_config

        mock_papers = [Mock(arxiv_id='1'), Mock(arxiv_id='2'), Mock(arxiv_id='3')]
        mock_arxiv = Mock()
        mock_arxiv.search_papers.return_value = mock_papers
        mock_arxiv_class.return_value = mock_arxiv

        mock_gemini = Mock()
        mock_gemini.summarize.side_effect = [
            Mock(),
            Exception("API error"),
            Mock(),
        ]
        mock_gemini_class.return_value = mock_gemini

        mock_notifier = Mock()
        mock_notifier_class.return_value = mock_notifier

        result = main()

        assert result == 0
        assert mock_notifier.send_all.call_count == 1
        sent_summaries = mock_notifier.send_all.call_args[0][0]
        assert len(sent_summaries) == 2

    @patch('arxiv_agent.main.load_config')
    @patch('arxiv_agent.main.setup_logger')
    @patch('sys.argv', ['main.py', 'config/test.yaml'])
    def test_main_config_load_failure(self, mock_logger, mock_load_config):
        """Should return 1 when config loading fails."""
        mock_load_config.side_effect = FileNotFoundError("Config not found")

        result = main()

        assert result == 1

    @patch('arxiv_agent.main.load_config')
    @patch('arxiv_agent.main.ArxivClient')
    @patch('arxiv_agent.main.GeminiClient')
    @patch('arxiv_agent.main.Notifier')
    @patch('arxiv_agent.main.setup_logger')
    @patch('sys.argv', ['main.py'])
    def test_main_default_config_path(self, mock_logger, mock_notifier_class,
                                       mock_gemini_class, mock_arxiv_class, mock_load_config):
        """Should use default config path when no argument provided."""
        mock_config = Mock()
        mock_config.arxiv.max_results = 10
        mock_config.arxiv.categories = ['cs.AI']
        mock_config.arxiv.keywords = ['LLM']
        mock_config.gemini.prompt_template = 'test template'
        mock_config.gemini.model = 'gemini-pro'
        mock_config.gemini.temperature = 0.7
        mock_config.gemini.max_tokens = 1000
        mock_config.notification = Mock()
        mock_load_config.return_value = mock_config

        mock_arxiv = Mock()
        mock_arxiv.search_papers.return_value = []
        mock_arxiv_class.return_value = mock_arxiv

        result = main()

        assert result == 0
        mock_load_config.assert_called_once_with('config/default.yaml')

    @patch('arxiv_agent.main.load_config')
    @patch('arxiv_agent.main.ArxivClient')
    @patch('arxiv_agent.main.GeminiClient')
    @patch('arxiv_agent.main.setup_logger')
    @patch('sys.argv', ['main.py', 'config/test.yaml'])
    def test_main_no_summaries_generated(self, mock_logger, mock_gemini_class,
                                          mock_arxiv_class, mock_load_config):
        """Should return 0 when all summarizations fail."""
        mock_config = Mock()
        mock_config.arxiv.max_results = 10
        mock_config.arxiv.categories = ['cs.AI']
        mock_config.arxiv.keywords = ['LLM']
        mock_config.gemini.prompt_template = 'test template'
        mock_config.gemini.model = 'gemini-pro'
        mock_config.gemini.temperature = 0.7
        mock_config.gemini.max_tokens = 1000
        mock_load_config.return_value = mock_config

        mock_papers = [Mock(arxiv_id='1'), Mock(arxiv_id='2')]
        mock_arxiv = Mock()
        mock_arxiv.search_papers.return_value = mock_papers
        mock_arxiv_class.return_value = mock_arxiv

        mock_gemini = Mock()
        mock_gemini.summarize.side_effect = [
            Exception("API error 1"),
            Exception("API error 2"),
        ]
        mock_gemini_class.return_value = mock_gemini

        result = main()

        assert result == 0
