"""State management for book writing workflow."""

from typing import Dict, Optional, Any
from enum import Enum
from loguru import logger
import json
from pathlib import Path


class WorkflowState(str, Enum):
    """Workflow state enumeration."""
    INITIALIZED = "initialized"
    PROFILE_CREATED = "profile_created"
    TYPE_DETERMINED = "type_determined"
    TOC_GENERATED = "toc_generated"
    CHAPTERS_WRITING = "chapters_writing"
    CHAPTERS_WRITTEN = "chapters_written"
    EXPANSION_DONE = "expansion_done"
    IMAGES_GENERATED = "images_generated"
    LATEX_GENERATED = "latex_generated"
    HUMANIZED = "humanized"
    QA_PASSED = "qa_passed"
    COMPILED = "compiled"
    COMPLETED = "completed"
    FAILED = "failed"


class StateManager:
    """Manages workflow state."""

    def __init__(self, state_file: Optional[Path] = None):
        """Initialize state manager.

        Args:
            state_file: Path to state file for persistence
        """
        self.state_file = state_file
        self.state = WorkflowState.INITIALIZED
        self.data: Dict[str, Any] = {}
        self.history = []

    def set_state(self, new_state: WorkflowState, data: Optional[Dict] = None) -> None:
        """Set workflow state.

        Args:
            new_state: New state
            data: Optional state data
        """
        logger.info(f"State transition: {self.state.value} -> {new_state.value}")
        self.history.append(self.state.value)
        self.state = new_state

        if data:
            self.data.update(data)

        self._save_state()

    def get_state(self) -> WorkflowState:
        """Get current state.

        Returns:
            Current state
        """
        return self.state

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get state data.

        Args:
            key: Data key
            default: Default value

        Returns:
            Data value
        """
        return self.data.get(key, default)

    def set_data(self, key: str, value: Any) -> None:
        """Set state data.

        Args:
            key: Data key
            value: Data value
        """
        self.data[key] = value
        self._save_state()

    def reset(self) -> None:
        """Reset state."""
        self.state = WorkflowState.INITIALIZED
        self.data = {}
        self.history = []
        self._save_state()
        logger.info("State reset")

    def _save_state(self) -> None:
        """Save state to file."""
        if not self.state_file:
            return

        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        state_data = {
            "state": self.state.value,
            "data": self.data,
            "history": self.history,
        }

        with open(self.state_file, "w") as f:
            json.dump(state_data, f, indent=2)

    def load_state(self) -> None:
        """Load state from file."""
        if not self.state_file or not self.state_file.exists():
            return

        with open(self.state_file, "r") as f:
            state_data = json.load(f)

        self.state = WorkflowState(state_data.get("state", "initialized"))
        self.data = state_data.get("data", {})
        self.history = state_data.get("history", [])
        logger.info(f"State loaded: {self.state.value}")
