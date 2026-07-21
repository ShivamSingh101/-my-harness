from ..base import BaseTool


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Write text to a file in the workspace. Requires user confirmation."

    def schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path relative to workspace",
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write",
                        },
                    },
                    "required": ["path", "content"],
                },
            },
        }

    def execute(self, path: str, content: str) -> str:
        target = self.context.safe_path(path)
        print(f"Tool request: write_file -> {target}")
        confirm = input("Allow write? y/n: ").strip().lower()
        if confirm != "y":
            return "Write denied by user"

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Wrote file: {path}"
