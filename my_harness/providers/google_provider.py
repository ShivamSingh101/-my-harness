import os

from .base import LLMProvider


class GoogleProvider(LLMProvider):
    def __init__(self, model=None, api_key=None):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("Google provider requires: pip install openai") from exc

        key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.client = OpenAI(
            api_key=key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        self.model = model or os.getenv("GEMINI_MODEL") or os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")

    def chat(self, messages, tools):
        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        return self.client.chat.completions.create(**kwargs)
