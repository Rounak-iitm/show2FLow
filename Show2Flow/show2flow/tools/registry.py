"""Central registry mapping tool names -> tool instances, and actions
to callables on those instances. Keeping this indirection is what lets
the executor stay agnostic of which concrete library (Playwright,
Browser Use, Unstructured, ...) backs a given tool.
"""
from __future__ import annotations

from typing import Any, Callable, Dict


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Any] = {}

    def register(self, name: str, tool_instance: Any) -> None:
        self._tools[name] = tool_instance

    def get(self, name: str) -> Any:
        if name not in self._tools:
            raise KeyError(
                f"Tool '{name}' is not registered. Registered tools: {list(self._tools)}"
            )
        return self._tools[name]

    def resolve_action(self, tool_name: str, action_name: str) -> Callable:
        tool = self.get(tool_name)
        if not hasattr(tool, action_name):
            raise AttributeError(f"Tool '{tool_name}' has no action '{action_name}'")
        return getattr(tool, action_name)

    def describe(self) -> Dict[str, Any]:
        """Return a manifest of tools/actions — used by the MCP server to
        expose Show2Flow's tools to other agents."""
        manifest = {}
        for name, tool in self._tools.items():
            actions = [
                m for m in dir(tool)
                if not m.startswith("_") and callable(getattr(tool, m))
            ]
            manifest[name] = actions
        return manifest


def default_registry() -> ToolRegistry:
    """Builds the standard registry used by the CLI/executor."""
    from show2flow.tools.browser import BrowserTool
    from show2flow.tools.files import FileTool
    from show2flow.tools.documents import DocumentTool

    reg = ToolRegistry()
    reg.register("browser", BrowserTool())
    reg.register("files", FileTool())
    reg.register("documents", DocumentTool())
    return reg
