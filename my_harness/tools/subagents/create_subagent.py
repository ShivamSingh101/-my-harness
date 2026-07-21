from ..base import BaseTool


class CreateSubagentTool(BaseTool):
    name = "create_subagent"
    description = "Create a focused subagent with its own session to investigate a subtask."

    def __init__(self, context, llm_provider, session_store, enable_bash=False):
        super().__init__(context)
        self.llm_provider = llm_provider
        self.session_store = session_store
        self.enable_bash = enable_bash

    def schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Short name for the subagent role, e.g. reviewer or investigator",
                        },
                        "task": {
                            "type": "string",
                            "description": "Specific task the subagent should complete",
                        },
                        "context": {
                            "type": "string",
                            "description": "Relevant context to give the subagent",
                        },
                    },
                    "required": ["name", "task"],
                },
            },
        }

    def execute(self, name: str, task: str, context: str = "") -> str:
        # Lazy imports avoid circular imports at package load time.
        from ...agent import Agent
        from ...session import Session
        from ..runner import ToolRunner

        session_data = self.session_store.create(kind="subagent", parent_name=name)
        session = Session(self.session_store, session_data)

        # Subagents get normal file tools and optional bash, but not create_subagent,
        # to avoid accidental infinite subagent nesting.
        subagent_tools = ToolRunner(
            workspace=self.context.workspace,
            enable_bash=self.enable_bash,
        )

        subagent = Agent(
            llm_provider=self.llm_provider,
            tools=subagent_tools,
            session=session,
            system_prompt=(
                f"You are a focused subagent named {name}.\n"
                "Work only on the delegated task. Be concise. "
                "Return findings and do not continue chatting."
            ),
        )

        prompt = f"Task:\n{task}\n\nContext:\n{context}"
        result = subagent.handle(prompt)

        return (
            f"Subagent '{name}' completed.\n"
            f"Session ID: {session.id}\n\n"
            f"Result:\n{result}"
        )
