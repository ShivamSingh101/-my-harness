import os

from openai import OpenAI

from .base import LLMProvider


class OpenRouterProvider(LLMProvider):
    def __init__(self, model=None, api_key=None):
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
        self.model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

    def chat(self, messages, tools):
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
