"""Logging configuration."""
import logging
import sys


def setup_logger() -> None:
    """Configure application logger."""
    numeric_level = logging.INFO

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
