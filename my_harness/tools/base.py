from abc import ABC, abstractmethod
from pathlib import Path


class ToolContext:
    """Shared context available to every tool."""

    def __init__(self, workspace="."):
        self.workspace = Path(workspace).resolve()

    def safe_path(self, path: str) -> Path:
        """Resolve a path and prevent escaping outside the workspace."""
        target = (self.workspace / path).resolve()

        if self.workspace not in target.parents and target != self.workspace:
            raise ValueError("Path is outside the workspace")

        return target


class BaseTool(ABC):
    """Base class for all tools."""

    name = None
    description = None

    def __init__(self, context: ToolContext):
        self.context = context

    @abstractmethod
    def schema(self) -> dict:
        """Return OpenAI-compatible tool schema."""
        raise NotImplementedError

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Run the tool and return text result."""
        raise NotImplementedError
