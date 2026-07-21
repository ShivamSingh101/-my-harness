# Packaging and Sharing My Harness

This project is packaged as a Python command-line application.

## Important naming note

Python package/terminal commands should not contain spaces. So the package is named:

```text
my-harness
```

and it installs these terminal commands:

```bash
my-harness
myharness
```

A command literally named `my harness` is not practical because shells treat spaces as argument separators. If you really want that style, create a shell alias/function, but `my-harness` is the normal approach.

## Project layout

```text
custom harness/
  pyproject.toml          Package metadata and CLI command config
  MANIFEST.in             Extra files included in source distribution
  README.md               Main documentation shown on PyPI/GitHub
  .env.example            Example environment config
  my_harness/             Installable Python package
    __init__.py
    main.py               CLI entrypoint
    agent.py              Agent loop
    session.py            Session storage
    prompts/              Agent instruction files and loader
    skills/               Agent skill instruction files, including subagents
    tools/                Scalable tool registry and tool folders
      base.py             BaseTool and ToolContext
      runner.py           Tool registry/executor
      filesystem/         File tools
      shell/              Shell tools
      subagents/          Subagent creation tool
    providers/            LLM providers
  docs/
    packaging.md          This guide
```

## Install locally for development

From the project folder:

```bash
cd "C:/Users/shiva/Downloads/custom harness"
python -m venv .venv
.venv/Scripts/activate
python -m pip install --upgrade pip
pip install -e .
```

Now you can run it from any terminal directory:

```bash
my-harness
```

Use a specific workspace:

```bash
my-harness --workspace "C:/path/to/project"
```

or:

```bash
myharness
```

## Workspace restriction

File tools are restricted to the configured workspace using `ToolContext.safe_path()` in:

```text
my_harness/tools/base.py
```

By default, these tools are enabled:

- `read_file`
- `write_file`

The `bash` tool is disabled by default because shell commands are not a reliable workspace sandbox. Enable it only when needed:

```bash
my-harness --enable-bash
```

For strong isolation, run the whole app inside Docker or a VM.

Sessions are stored inside:

```text
<workspace>/.my_harness/sessions/
```

## Agent instructions / prompt folder

Prompt files are stored in:

```text
my_harness/prompts/system.md
my_harness/prompts/prompt.md
```

Meaning:

- `system.md` = common instructions for all agents
- `prompt.md` = specialized user/project instructions

Use custom prompt files:

```bash
my-harness --system-prompt ./system.md --user-prompt ./prompt.md
```

Or set environment variables:

```env
MY_HARNESS_SYSTEM_PROMPT=C:/path/to/system.md
MY_HARNESS_USER_PROMPT=C:/path/to/prompt.md
```

## Configure OpenAI/API keys after install

If no API key is configured, chat will not start. The user must complete model setup first.

Interactive setup:

```bash
my-harness --setup-model
```

Inside chat:

```text
/model
```

Currently supported provider: `openai`.

OpenAI model options shown by setup:

```text
gpt-4o-mini
gpt-4o
gpt-4.1-mini
gpt-4.1
o4-mini
```

Recommended per-workspace setup:

```bash
my-harness --workspace "C:/path/to/project" --init-config
```

This creates:

```text
<workspace>/.env
```

Edit it and add your key.

Manual setup: create a `.env` file in the directory where you run the command or in the selected workspace:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

The app loads `.env` from your current working directory and from the selected workspace.

You can also set environment variables globally.

Windows PowerShell:

```powershell
setx OPENAI_API_KEY "your_api_key_here"
```

macOS/Linux:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

## Subagents

Subagents are enabled by default through the `create_subagent` tool.

Disable them with:

```bash
my-harness --no-subagents
```

The subagent skill instructions are stored in:

```text
my_harness/skills/subagents.md
```

A subagent gets its own session with `kind: subagent`, stored in:

```text
<workspace>/.my_harness/sessions/
```

## Add more tools

Tools are now organized by category:

```text
my_harness/tools/
  base.py
  runner.py
  filesystem/
    read_file.py
    write_file.py
  shell/
    bash.py
```

Each tool extends `BaseTool` and implements:

- `schema()` - OpenAI-compatible tool schema
- `execute()` - actual tool behavior

After creating a tool class, register it in `my_harness/tools/runner.py`.

## Build distributable files

Install build tools:

```bash
pip install build twine
```

Build:

```bash
python -m build
```

This creates:

```text
dist/my_harness-0.1.0.tar.gz
dist/my_harness-0.1.0-py3-none-any.whl
```

## Install on another system from wheel

Copy the `.whl` file to another machine, then run:

```bash
pip install my_harness-0.1.0-py3-none-any.whl
```

Then use:

```bash
my-harness
```

## Publish to PyPI

Create an account on PyPI, then:

```bash
python -m build
python -m twine upload dist/*
```

After publishing, anyone can install it with:

```bash
pip install my-harness
```

## Publish to TestPyPI first

Recommended before real PyPI:

```bash
python -m twine upload --repository testpypi dist/*
```

Install from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ my-harness
```

## How terminal command creation works

In `pyproject.toml`:

```toml
[project.scripts]
my-harness = "my_harness.main:main"
myharness = "my_harness.main:main"
```

This means after install, Python creates terminal commands that call:

```python
my_harness.main.main()
```
