from ..base import BaseTool


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read a text file from the workspace."

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
                        }
                    },
                    "required": ["path"],
                },
            },
        }

    def execute(self, path: str) -> str:
        target = self.context.safe_path(path)
        if not target.exists():
            return f"File not found: {path}"
        if not target.is_file():
            return f"Not a file: {path}"
        return target.read_text(encoding="utf-8")
