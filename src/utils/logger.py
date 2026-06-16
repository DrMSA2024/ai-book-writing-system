"""Logging setup utility."""

from pathlib import Path
from loguru import logger
import sys


def setup_logger(log_dir: Path, level: str = "INFO") -> None:
    """Setup logging configuration.

    Args:
        log_dir: Directory for log files
        level: Log level
    """
    log_dir.mkdir(parents=True, exist_ok=True)

    # Remove default handler
    logger.remove()

    # Add file handler
    logger.add(
        log_dir / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=level,
        rotation="500 MB",
        retention="7 days",
    )

    # Add console handler
    logger.add(
        sys.stderr,
        format="{time:HH:mm:ss} | {level: <8} | {message}",
        level=level,
    )
