import os

from .openai_provider import OpenAIProvider
from .openrouter_provider import OpenRouterProvider
# from .google_provider import GoogleProvider


SUPPORTED_PROVIDERS = {
    "openai": OpenAIProvider,
    "openrouter": OpenRouterProvider,
    # "google": GoogleProvider,
}


def create_llm_provider(provider_name=None, model=None):
    """
    Factory for LLM providers.

    Add more providers by:
    1. creating providers/my_provider.py
    2. implementing LLMProvider
    3. registering it in SUPPORTED_PROVIDERS
    """
    provider_name = (provider_name or os.getenv("LLM_PROVIDER", "openai")).lower()

    provider_cls = SUPPORTED_PROVIDERS.get(provider_name)
    if not provider_cls:
        available = ", ".join(SUPPORTED_PROVIDERS.keys())
        raise ValueError(f"Unsupported provider '{provider_name}'. Available: {available}")

    return provider_cls(model=model)
