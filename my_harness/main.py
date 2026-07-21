import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

from .agent import Agent
from .config import has_required_config, run_model_setup
from .providers import create_llm_provider
from .session import Session, SessionStore
from .tools import ToolRunner
from .tools.subagents import CreateSubagentTool


def parse_args():
    parser = argparse.ArgumentParser(description="Custom AI agent harness")
    parser.add_argument("--provider", default=None, help="LLM provider, e.g. openai")
    parser.add_argument("--model", default=None, help="Model name")
    parser.add_argument("--session", default=None, help="Existing session ID to resume")
    parser.add_argument("--list-sessions", action="store_true", help="List saved sessions")
    parser.add_argument("--system-prompt", default=None, help="Path to common system.md instructions")
    parser.add_argument("--user-prompt", default=None, help="Path to specialized prompt.md instructions")
    parser.add_argument("--workspace", default=".", help="Directory the agent tools can access")
    parser.add_argument("--enable-bash", action="store_true", help="Enable bash tool. Not workspace-safe without OS sandboxing.")
    parser.add_argument("--no-subagents", action="store_true", help="Disable create_subagent tool")
    parser.add_argument("--init-config", action="store_true", help="Create a local .env file for API keys")
    parser.add_argument("--setup-model", action="store_true", help="Run interactive model/API-key setup")
    return parser.parse_args()


def create_env_file(workspace):
    env_path = workspace / ".env"
    if env_path.exists():
        print(f"Config already exists: {env_path}")
        return
    env_path.write_text(
        "LLM_PROVIDER=openai\n"
        "OPENAI_API_KEY=your_api_key_here\n"
        "OPENAI_MODEL=gpt-4o-mini\n"
        "# Optional:\n"
        "# MY_HARNESS_SYSTEM_PROMPT=C:/path/to/system.md\n"
        "# MY_HARNESS_USER_PROMPT=C:/path/to/prompt.md\n",
        encoding="utf-8",
    )
    print(f"Created config: {env_path}")
    print("Edit this file and add your API key.")


def build_agent(args, workspace, store, session):
    provider_name = args.provider or os.getenv("LLM_PROVIDER", "openai")
    model = args.model

    llm_provider = create_llm_provider(provider_name, model=model)
    tools = ToolRunner(workspace=workspace, enable_bash=args.enable_bash)

    if not args.no_subagents:
        tools.register(
            CreateSubagentTool(
                context=tools.context,
                llm_provider=llm_provider,
                session_store=store,
                enable_bash=args.enable_bash,
            )
        )

    agent = Agent(
        llm_provider=llm_provider,
        tools=tools,
        session=session,
        system_prompt_path=args.system_prompt,
        user_prompt_path=args.user_prompt,
    )
    return agent, provider_name


def print_slash_help():
    print("""
Slash commands:
/model          Setup or change provider/model/API key
/sessions       List saved sessions
/help           Show this help
/exit           Quit
""")


def main():
    args = parse_args()

    workspace = Path(args.workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    if args.init_config:
        create_env_file(workspace)
        return

    # Load .env from current directory and selected workspace.
    load_dotenv()
    load_dotenv(workspace / ".env")

    if args.setup_model:
        run_model_setup(workspace)
        load_dotenv(workspace / ".env", override=True)

    provider_name = args.provider or os.getenv("LLM_PROVIDER", "openai")
    if not has_required_config(provider_name):
        run_model_setup(workspace)
        load_dotenv(workspace / ".env", override=True)

    # Store sessions inside the selected workspace so each workspace has isolated history.
    store = SessionStore(workspace / ".my_harness" / "sessions")

    if args.list_sessions:
        sessions = store.list_sessions()
        if not sessions:
            print("No sessions found.")
            return
        for item in sessions:
            print(f"{item['id']} | kind={item['kind']} | messages={item['message_count']} | updated={item['updated_at']}")
        return

    session_data = store.load_or_create(args.session)
    session = Session(store, session_data)

    agent, provider_name = build_agent(args, workspace, store, session)

    print("Custom AI Harness")
    print(f"Provider: {provider_name}")
    print(f"Workspace: {workspace}")
    print(f"Bash enabled: {args.enable_bash}")
    print(f"Subagents enabled: {not args.no_subagents}")
    print(f"Session ID: {session.id}")
    print("Type '/help' for commands, '/exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit", "/exit", "/quit"]:
            print("Goodbye!")
            break

        if user_input == "/help":
            print_slash_help()
            continue

        if user_input == "/sessions":
            for item in store.list_sessions():
                print(f"{item['id']} | kind={item['kind']} | messages={item['message_count']} | updated={item['updated_at']}")
            continue

        if user_input == "/model":
            run_model_setup(workspace)
            load_dotenv(workspace / ".env", override=True)
            args.provider = os.getenv("LLM_PROVIDER", "openai")
            args.model = os.getenv("OPENAI_MODEL")
            agent, provider_name = build_agent(args, workspace, store, session)
            print(f"Model updated. Provider: {provider_name}, model: {args.model}\n")
            continue

        try:
            response = agent.handle(user_input)
            print(f"Agent: {response}\n")
        except KeyboardInterrupt:
            print("\nInterrupted. Type /exit to quit.\n")
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
