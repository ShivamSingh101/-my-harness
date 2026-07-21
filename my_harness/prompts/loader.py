import os
from importlib import resources
from pathlib import Path


DEFAULT_SYSTEM_PROMPT = "system.md"
DEFAULT_USER_PROMPT = "prompt.md"


def _read_packaged_prompt(file_name):
    return resources.files("my_harness.prompts").joinpath(file_name).read_text(encoding="utf-8")


def load_system_prompt(system_prompt_path=None, user_prompt_path=None):
    """
    Load agent instructions.

    system.md = common instructions for every agent.
    prompt.md = specialized user/project instructions.

    Priority for system.md:
    1. explicit system_prompt_path argument
    2. MY_HARNESS_SYSTEM_PROMPT environment variable
    3. packaged prompts/system.md

    Priority for prompt.md:
    1. explicit user_prompt_path argument
    2. MY_HARNESS_USER_PROMPT environment variable
    3. packaged prompts/prompt.md
    """
    system_prompt_path = system_prompt_path or os.getenv("MY_HARNESS_SYSTEM_PROMPT")
    user_prompt_path = user_prompt_path or os.getenv("MY_HARNESS_USER_PROMPT")

    if system_prompt_path:
        system_prompt = Path(system_prompt_path).read_text(encoding="utf-8")
    else:
        system_prompt = _read_packaged_prompt(DEFAULT_SYSTEM_PROMPT)

    if user_prompt_path:
        user_prompt = Path(user_prompt_path).read_text(encoding="utf-8")
    else:
        user_prompt = _read_packaged_prompt(DEFAULT_USER_PROMPT)

    return f"# Common Agent Instructions\n\n{system_prompt}\n\n# Specialized User Instructions\n\n{user_prompt}"
