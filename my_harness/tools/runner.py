from .base import ToolContext
from .filesystem.read_file import ReadFileTool
from .filesystem.write_file import WriteFileTool
from .shell.bash import BashTool


class ToolRunner:
    """
    Tool registry and executor.

    To add a tool:
    1. create a new BaseTool subclass
    2. import it here
    3. add it to default_tools
    """

    def __init__(self, workspace=".", tools=None, enable_bash=False):
        self.context = ToolContext(workspace=workspace)
        self.tools = {}

        if tools is None:
            default_tools = [
                ReadFileTool(self.context),
                WriteFileTool(self.context),
            ]
            if enable_bash:
                default_tools.append(BashTool(self.context))
        else:
            default_tools = tools

        for tool in default_tools:
            self.register(tool)

    def register(self, tool):
        if not tool.name:
            raise ValueError("Tool must have a name")
        self.tools[tool.name] = tool

    def schemas(self):
        return [tool.schema() for tool in self.tools.values()]

    def run(self, name, args):
        tool = self.tools.get(name)
        if not tool:
            return f"Unknown tool: {name}"

        try:
            return tool.execute(**args)
        except TypeError as e:
            return f"Invalid arguments for {name}: {e}"
        except Exception as e:
            return f"{name} error: {e}"

    # Convenience methods kept for compatibility.
    def read_file(self, path: str) -> str:
        return self.run("read_file", {"path": path})

    def write_file(self, path: str, content: str) -> str:
        return self.run("write_file", {"path": path, "content": content})

    def bash(self, command: str) -> str:
        return self.run("bash", {"command": command})
