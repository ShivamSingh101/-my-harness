import subprocess

from ..base import BaseTool


class BashTool(BaseTool):
    name = "bash"
    description = "Run a shell command in the workspace. Requires user confirmation."

    blocked_commands = [
        "rm -rf",
        "format",
        "shutdown",
        "del /s",
        "rmdir /s",
        ":(){",
    ]

    def schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Shell command to run",
                        }
                    },
                    "required": ["command"],
                },
            },
        }

    def execute(self, command: str) -> str:
        lower = command.lower()
        if any(item in lower for item in self.blocked_commands):
            return "Blocked dangerous command"

        print(f"Tool request: bash -> {command}")
        confirm = input("Allow command? y/n: ").strip().lower()
        if confirm != "y":
            return "Command denied by user"

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.context.workspace,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout + result.stderr
            return output if output.strip() else f"Command finished with code {result.returncode}"
        except subprocess.TimeoutExpired:
            return "Command timed out"
