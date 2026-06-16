"""Configuration management for book writing system."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the book writing system."""

    # API Configuration
    DEEPSEEK_API_KEY: str = os.getenv(
        "DEEPSEEK_API_KEY", "sk-your-key-here"
    )
    DEEPSEEK_API_BASE: str = os.getenv(
        "DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"
    )
    DEEPSEEK_MODEL: str = os.getenv(
        "DEEPSEEK_MODEL", "deepseek-chat"
    )

    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    BOOKS_DIR = DATA_DIR / "books"
    TEMP_DIR = PROJECT_ROOT / "temp"
    LOGS_DIR = PROJECT_ROOT / "logs"

    # Memory Configuration
    MEMORY_DB: str = os.getenv(
        "MEMORY_DB", str(DATA_DIR / "memory.db")
    )
    CHROMADB_PATH: str = os.getenv(
        "CHROMADB_PATH", str(DATA_DIR / "chromadb")
    )

    # LaTeX Configuration
    LATEXMK_PATH: str = os.getenv(
        "LATEXMK_PATH", "/usr/bin/latexmk"
    )
    PDFLATEX_PATH: str = os.getenv(
        "PDFLATEX_PATH", "/usr/bin/pdflatex"
    )

    # API Configuration
    API_RATE_LIMIT: int = int(os.getenv("API_RATE_LIMIT", "10"))
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "60"))
    MAX_RETRIES: int = 3
    RETRY_BACKOFF: float = 1.5

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Book Configuration
    DEFAULT_LANGUAGE: str = "English"
    DEFAULT_ENCODING: str = "utf-8"

    # Feature Flags
    AUTO_HUMANIZE: bool = True
    AUTO_QA_CHECK: bool = True
    AUTO_LATEX_CORRECTION: bool = True

    # Humanization Settings
    AI_SCORE_TARGET: float = 0.10  # Below 10%
    HUMANIZATION_LEVEL: str = "natural"  # natural, strict, slight_imperfections

    @classmethod
    def setup(cls) -> None:
        """Create necessary directories and setup logging."""
        # Create directories
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.BOOKS_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)

        # Setup logging
        logger.remove()
        logger.add(
            cls.LOGS_DIR / "app.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=cls.LOG_LEVEL,
            rotation="500 MB",
            retention="7 days",
        )
        logger.add(
            lambda msg: print(msg, end=""),
            format="{time:HH:mm:ss} | {level: <8} | {message}",
            level=cls.LOG_LEVEL,
        )

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration."""
        if not cls.DEEPSEEK_API_KEY or cls.DEEPSEEK_API_KEY == "sk-your-key-here":
            logger.warning("DeepSeek API key not configured")
            return False

        if not Path(cls.PDFLATEX_PATH).exists():
            logger.warning(f"pdflatex not found at {cls.PDFLATEX_PATH}")

        return True


# Initialize configuration
Config.setup()
