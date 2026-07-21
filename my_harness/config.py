import os
from pathlib import Path


OPENAI_MODEL_OPTIONS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4.1-mini",
    "gpt-4.1",
    "o4-mini",
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
    data["LLM_PROVIDER"] = provider

    if provider == "openai":
        data["OPENAI_API_KEY"] = api_key
        data["OPENAI_MODEL"] = model

    write_env_file(env_path, data)

    # Also update current process so setup works immediately.
    os.environ.update(data)
    return env_path


def has_required_config(provider):
    provider = (provider or os.getenv("LLM_PROVIDER", "openai")).lower()
    if provider == "openai":
        return bool(os.getenv("OPENAI_API_KEY"))
    return True


def run_model_setup(workspace):
    print("\nModel setup is required before chatting.\n")
    print("Available providers:")
    print("1. openai")

    provider_choice = input("Provider [openai]: ").strip().lower() or "openai"
    if provider_choice not in ["openai"]:
        print("Only OpenAI is currently implemented. Using openai.")
        provider_choice = "openai"

    print("\nOpenAI model options:")
    for index, model_name in enumerate(OPENAI_MODEL_OPTIONS, start=1):
        print(f"{index}. {model_name}")

    selected = input("Choose model number or paste model name [1]: ").strip()
    if not selected:
        model = OPENAI_MODEL_OPTIONS[0]
    elif selected.isdigit() and 1 <= int(selected) <= len(OPENAI_MODEL_OPTIONS):
        model = OPENAI_MODEL_OPTIONS[int(selected) - 1]
    else:
        model = selected

    api_key = input("Paste OpenAI API key: ").strip()
    while not api_key:
        print("API key is required.")
        api_key = input("Paste OpenAI API key: ").strip()

    env_path = save_model_config(workspace, provider_choice, model, api_key)
    print(f"\nSaved model config to: {env_path}\n")
    return provider_choice, model
