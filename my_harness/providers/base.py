from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Base interface for all LLM providers."""

    @abstractmethod
    def chat(self, messages, tools):
        """Return a provider response for the given messages and tool schemas."""
        raise NotImplementedError
