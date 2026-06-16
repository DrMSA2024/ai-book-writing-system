"""Base agent class for all agents."""

from abc import ABC, abstractmethod
from typing import Any, Optional
from loguru import logger
from src.api.deepseek_client import DeepSeekClient
from src.memory.memory_manager import MemoryManager


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(
        self,
        name: str,
        description: str,
        api_client: Optional[DeepSeekClient] = None,
        memory_manager: Optional[MemoryManager] = None,
    ):
        """Initialize base agent.

        Args:
            name: Agent name
            description: Agent description
            api_client: DeepSeek API client
            memory_manager: Memory manager instance
        """
        self.name = name
        self.description = description
        self.api_client = api_client
        self.memory_manager = memory_manager
        logger.info(f"Initialized agent: {name}")

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Execute agent task.

        Must be implemented by subclasses.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Task result
        """
        pass

    def log_info(self, message: str) -> None:
        """Log info message.

        Args:
            message: Message to log
        """
        logger.info(f"[{self.name}] {message}")

    def log_error(self, message: str) -> None:
        """Log error message.

        Args:
            message: Message to log
        """
        logger.error(f"[{self.name}] {message}")

    def log_debug(self, message: str) -> None:
        """Log debug message.

        Args:
            message: Message to log
        """
        logger.debug(f"[{self.name}] {message}")
