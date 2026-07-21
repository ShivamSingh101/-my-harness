import json

from .prompts import load_system_prompt
from .skills import load_skills_text


class Agent:
    """
    Provider-independent agent.

    The LLM provider only needs a chat(messages, tools) method.
    Session owns the persistent message history.
    """

    def __init__(self, llm_provider, tools, session, system_prompt_path=None, user_prompt_path=None, system_prompt=None):
        self.llm = llm_provider
        self.tools = tools
        self.session = session

        if not self.session.messages:
            base_prompt = system_prompt or load_system_prompt(system_prompt_path, user_prompt_path)
            full_prompt = f"{base_prompt}\n\n# Available Skills\n\n{load_skills_text()}"
            self.session.messages = [
                {
                    "role": "system",
                    "content": full_prompt,
                }
            ]
            self.session.save()

    def handle(self, user_input: str) -> str:
        self.session.messages.append({"role": "user", "content": user_input})

        while True:
            response = self.llm.chat(self.session.messages, self.tool_schemas())
            message = response.choices[0].message

            assistant_message = {
                "role": "assistant",
                "content": message.content,
            }

            if message.tool_calls:
                assistant_message["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ]

            self.session.messages.append(assistant_message)

            if not message.tool_calls:
                final = message.content or ""
                self.session.save()
                return final

            for tool_call in message.tool_calls:
                result = self.run_tool_call(tool_call)
                self.session.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )
                self.session.save()

    def run_tool_call(self, tool_call) -> str:
        name = tool_call.function.name

        try:
            args = json.loads(tool_call.function.arguments or "{}")
        except json.JSONDecodeError:
            return "Invalid tool arguments JSON"

        return self.tools.run(name, args)

    def tool_schemas(self):
        return self.tools.schemas()
