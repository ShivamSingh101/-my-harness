import os

from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, model=None, api_key=None):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("OpenAI provider requires: pip install openai") from exc

        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def chat(self, messages, tools):
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
