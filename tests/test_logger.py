"""Tests for logger configuration."""
import pytest
import logging
import sys
from unittest.mock import patch, MagicMock, call
from arxiv_agent.utils.logger import setup_logger


class TestLogger:
    """Test cases for logger setup."""

    def test_setup_logger_configures_info_level(self):
        """Should configure logger at INFO level."""
        with patch('logging.basicConfig') as mock_basicConfig:
            setup_logger()

            mock_basicConfig.assert_called_once()
            call_kwargs = mock_basicConfig.call_args[1]
            assert call_kwargs['level'] == logging.INFO

    def test_setup_logger_configures_format(self):
        """Should configure logger with proper format."""
        with patch('logging.basicConfig') as mock_basicConfig:
            setup_logger()

            call_kwargs = mock_basicConfig.call_args[1]
            assert 'asctime' in call_kwargs['format']
            assert 'name' in call_kwargs['format']
            assert 'levelname' in call_kwargs['format']
            assert 'message' in call_kwargs['format']

    def test_setup_logger_uses_stdout(self):
        """Should configure logger to output to stdout."""
        with patch('logging.basicConfig') as mock_basicConfig:
            setup_logger()

            call_kwargs = mock_basicConfig.call_args[1]
            handlers = call_kwargs['handlers']
            assert len(handlers) == 1
            assert isinstance(handlers[0], logging.StreamHandler)
            assert handlers[0].stream == sys.stdout
