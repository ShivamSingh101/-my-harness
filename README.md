# My Harness

My Harness is a small educational AI agent harness.

It has:

- terminal CLI command: `my-harness`
- pluggable LLM providers
- OpenAI, Google (Gemini), and OpenRouter providers included
- session creation/resume/listing
- session storage as JSON
- tool-calling loop
- scalable tools folder structure
- prompt folder for agent instructions
- skills folder for optional agent behaviors
- subagent creation tool
- workspace-restricted file tools
- bash disabled by default
- tools: `read_file`, `write_file`, optional `bash`

## Install for local development

```bash
cd "C:/Users/shiva/Downloads/custom harness"
python -m venv .venv
.venv/Scripts/activate
python -m pip install --upgrade pip
pip install -e .
```

Now run from anywhere:

```bash
my-harness
```

or:

```bash
myharness
```

> A command with a space like `my harness` is not recommended because terminals treat spaces as separators. Use `my-harness`.

## Configure

After installing, users can create API key config with:

```bash
my-harness --workspace "C:/path/to/project" --init-config
```

This creates:

```text
<workspace>/.env
```

Then edit that file and add the API key.

Alternatively, manually create `.env` in the folder where you run `my-harness` or inside the selected workspace:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Or set the API key globally in your shell.

Windows PowerShell:

```powershell
setx OPENAI_API_KEY "your_api_key_here"
```

macOS/Linux:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

You can copy the example:

```bash
copy .env.example .env
```

## Usage

Create a new session in the current folder as workspace:

```bash
my-harness
```

Use a specific workspace:

```bash
my-harness --workspace "C:/path/to/project"
```

List sessions in current folder:

```bash
my-harness --list-sessions
```

Resume a session:

```bash
my-harness --session <session-id>
```

Choose provider/model:

```bash
my-harness --provider openai --model gpt-4o-mini
```

Interactive model/API-key setup:

```bash
my-harness --setup-model
```

Inside chat, use:

```text
/model
```

Currently supported providers: `openai`, `google` (or `gemini`), `openrouter`.

### Provider Configuration & Models:

1. **OpenAI** (`LLM_PROVIDER=openai`)
   - Env Vars: `OPENAI_API_KEY`, `OPENAI_MODEL`
   - Models: `gpt-4o-mini`, `gpt-4o`, `gpt-4.1-mini`, `gpt-4.1`, `o4-mini`

2. **Google Gemini** (`LLM_PROVIDER=google`)
   - Env Vars: `GEMINI_API_KEY` (or `GOOGLE_API_KEY`), `GEMINI_MODEL`
   - Models: `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`

3. **OpenRouter** (`LLM_PROVIDER=openrouter`)
   - Env Vars: `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`
   - Models: `anthropic/claude-3.5-sonnet`, `openai/gpt-4o-mini`, `google/gemini-2.5-flash`, `deepseek/deepseek-chat`, `meta-llama/llama-3.3-70b-instruct`

If API keys are missing, chat will not start. The setup flow asks the user to paste the key first.

Disable subagents if you do not want the agent to spawn focused helper agents:

```bash
my-harness --no-subagents
```

Enable bash if you need shell commands:

```bash
my-harness --enable-bash
```

Important: `read_file` and `write_file` are restricted to the workspace. `bash` is not a strong workspace sandbox because shell commands can still try to access paths outside the workspace if your OS allows it. For strong isolation, run `my-harness` inside Docker/VM.

Use custom prompt files:

```bash
my-harness --system-prompt ./system.md --user-prompt ./prompt.md
```

Or set them in `.env`:

```env
MY_HARNESS_SYSTEM_PROMPT=C:/path/to/system.md
MY_HARNESS_USER_PROMPT=C:/path/to/prompt.md
```

Meaning:

- `system.md` = common agent instructions for all agents
- `prompt.md` = specialized user/project instructions

## Sessions

Sessions are stored inside the selected workspace:

```text
<workspace>/.my_harness/sessions/<session-id>.json
```

Each session contains:

```json
{
  "id": "uuid",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "messages": []
}
```

## Project structure

```text
custom harness/
  pyproject.toml
  MANIFEST.in
  README.md
  .env.example
  my_harness/
    __init__.py
    main.py
    agent.py
    session.py
    llm.py
    prompts/
      __init__.py
      loader.py
      system.md
      prompt.md
    skills/
      __init__.py
      loader.py
      subagents.md
    providers/
      __init__.py
      base.py
      factory.py
      openai_provider.py
      google_provider.py
      openrouter_provider.py
    tools/
      __init__.py
      base.py
      runner.py
      filesystem/
        read_file.py
        write_file.py
      shell/
        bash.py
      subagents/
        create_subagent.py
  docs/
    packaging.md
```

## Add another tool

Create a new file under `my_harness/tools/`, for example:

```text
my_harness/tools/network/http_get.py
```

Implement `BaseTool`:

```python
from ..base import BaseTool

class HttpGetTool(BaseTool):
    name = "http_get"
    description = "Fetch a URL."

    def schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {"url": {"type": "string"}},
                    "required": ["url"],
                },
            },
        }

    def execute(self, url: str) -> str:
        return "TODO: fetch URL"
```

Then register it in `my_harness/tools/runner.py`.

## Skills and subagents

Skill instructions live in:

```text
my_harness/skills/
```

The included skill file is:

```text
my_harness/skills/subagents.md
```

It teaches the main agent when to use the `create_subagent` tool.

The subagent tool:

- creates a separate session
- gives the subagent a focused task
- lets it use workspace-safe tools
- returns the result to the main agent

Subagent sessions are stored in the same workspace session folder and marked with:

```json
"kind": "subagent"
```

## Agent prompts

Default instructions live in:

```text
my_harness/prompts/system.md
```

You can edit that file during development, or pass a custom prompt at runtime:

```bash
my-harness --system-prompt ./system.md
```

## Add another LLM provider

Create:

```text
my_harness/providers/my_provider.py
```

Example:

```python
from .base import LLMProvider

class MyProvider(LLMProvider):
    def __init__(self, model=None):
        self.model = model or "my-default-model"

    def chat(self, messages, tools):
        # Call your provider API here.
        # Return a response compatible with agent.py.
        pass
```

Register it in `my_harness/providers/factory.py`:

```python
from .my_provider import MyProvider

SUPPORTED_PROVIDERS = {
    "openai": OpenAIProvider,
    "myprovider": MyProvider,
}
```

Then run:

```bash
my-harness --provider myprovider
```

## Build package

```bash
pip install build twine
python -m build
```

Output appears in:

```text
dist/
```

Install the wheel on another system:

```bash
pip install dist/my_harness-0.1.0-py3-none-any.whl
```

## Contributors

See:

```text
CONTRIBUTORS.md
```

## More docs

See:

```text
docs/packaging.md
```

## Workspace access and safety

File access is controlled in `my_harness/tools/base.py` using `ToolContext.safe_path()`.

This blocks paths like:

```text
../secret.txt
C:/Users/shiva/secret.txt
```

when they are outside the configured workspace.

By default, only workspace-safe file tools are enabled:

- `read_file`
- `write_file`

The `bash` tool is disabled by default. Enable it only when needed:

```bash
my-harness --enable-bash
```

For true security, use Docker/VM/container isolation.
