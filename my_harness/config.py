import os
from pathlib import Path


OPENAI_MODEL_OPTIONS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4.1-mini",
    "gpt-4.1",
    "o4-mini",
]

GOOGLE_MODEL_OPTIONS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

OPENROUTER_MODEL_OPTIONS = [
    "openai/gpt-4o-mini",
    "anthropic/claude-3.5-sonnet",
    "google/gemini-2.0-flash-001",
]


def env_path_for_workspace(workspace):
    return Path(workspace).resolve() / ".env"


def read_env_file(path):
    data = {}
    path = Path(path)
    if not path.exists():
        return data

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def write_env_file(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}={value}" for key, value in data.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_model_config(workspace, provider, model, api_key):
    env_path = env_path_for_workspace(workspace)
    data = read_env_file(env_path)
    provider = provider.lower()
    data["LLM_PROVIDER"] = provider

    if provider == "openai":
        data["OPENAI_API_KEY"] = api_key
        data["OPENAI_MODEL"] = model
    elif provider in ["google", "gemini"]:
        data["GEMINI_API_KEY"] = api_key
        data["GEMINI_MODEL"] = model
    elif provider == "openrouter":
        data["OPENROUTER_API_KEY"] = api_key
        data["OPENROUTER_MODEL"] = model

    write_env_file(env_path, data)

    # Also update current process so setup works immediately.
    os.environ.update(data)
    return env_path


def has_required_config(provider):
    provider = (provider or os.getenv("LLM_PROVIDER", "openai")).lower()
    if provider == "openai":
        return bool(os.getenv("OPENAI_API_KEY"))
    if provider in ["google", "gemini"]:
        return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    if provider == "openrouter":
        return bool(os.getenv("OPENROUTER_API_KEY"))
    return True


def run_model_setup(workspace):
    print("\nModel setup is required before chatting.\n")
    print("Available providers:")
    print("1. openai")
    print("2. google")
    print("3. openrouter")

    provider_input = input("Provider [openai]: ").strip().lower() or "openai"
    provider_map = {
        "1": "openai",
        "openai": "openai",
        "2": "google",
        "google": "google",
        "gemini": "google",
        "3": "openrouter",
        "openrouter": "openrouter",
    }
    provider_choice = provider_map.get(provider_input)
    if not provider_choice:
        print(f"Unknown provider '{provider_input}'. Defaulting to openai.")
        provider_choice = "openai"

    if provider_choice == "openai":
        model_options = OPENAI_MODEL_OPTIONS
        key_name = "OpenAI API key"
    elif provider_choice == "google":
        model_options = GOOGLE_MODEL_OPTIONS
        key_name = "Gemini/Google API key"
    elif provider_choice == "openrouter":
        model_options = OPENROUTER_MODEL_OPTIONS
        key_name = "OpenRouter API key"

    print(f"\n{provider_choice.capitalize()} model options:")
    for index, model_name in enumerate(model_options, start=1):
        print(f"{index}. {model_name}")

    selected = input("Choose model number or paste model name [1]: ").strip()
    if not selected:
        model = model_options[0]
    elif selected.isdigit() and 1 <= int(selected) <= len(model_options):
        model = model_options[int(selected) - 1]
    else:
        model = selected

    api_key = input(f"Paste {key_name}: ").strip()
    while not api_key:
        print("API key is required.")
        api_key = input(f"Paste {key_name}: ").strip()

    env_path = save_model_config(workspace, provider_choice, model, api_key)
    print(f"\nSaved model config to: {env_path}\n")
    return provider_choice, model
