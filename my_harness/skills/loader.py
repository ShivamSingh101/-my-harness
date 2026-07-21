from importlib import resources


SKILL_FILES = [
    "subagents.md",
]


def load_skills_text():
    """Load packaged skill instruction files and combine them."""
    parts = []
    skill_package = resources.files("my_harness.skills")

    for file_name in SKILL_FILES:
        content = skill_package.joinpath(file_name).read_text(encoding="utf-8")
        parts.append(f"# Skill: {file_name}\n\n{content}")

    return "\n\n".join(parts)
