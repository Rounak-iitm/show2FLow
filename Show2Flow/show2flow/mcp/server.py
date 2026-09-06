"""Exposes Show2Flow's tools and workflows over MCP (Model Context
Protocol), using the official Python SDK, so other agents can call
`show2flow.run_workflow`, `show2flow.browser.extract`, etc.

Requires: pip install "mcp[cli]"
Run with:  python -m show2flow.mcp.server
"""
from __future__ import annotations

import json

from show2flow.core.executor import run_workflow
from show2flow.core.recorder import load_workflow
from show2flow.tools.registry import default_registry

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as e:  # pragma: no cover
    raise SystemExit(
        "The 'mcp' package is not installed. Run: pip install \"mcp[cli]\""
    ) from e


mcp = FastMCP("show2flow")
_registry = default_registry()


@mcp.tool()
def run_named_workflow(workflow_path: str) -> str:
    """Run a Show2Flow workflow YAML file by path (or name under
    workflows/examples/) and return a JSON summary of the run."""
    workflow = load_workflow(workflow_path)
    state = run_workflow(workflow, registry=_registry)
    return json.dumps(state.summary())


@mcp.tool()
def browser_open(url: str) -> str:
    """Open a URL in the Show2Flow-managed browser."""
    return json.dumps(_registry.get("browser").open(url))


@mcp.tool()
def browser_extract(selector: str, limit: int = 20) -> str:
    """Extract text from every element matching a CSS selector on the
    current page."""
    return json.dumps(_registry.get("browser").extract(selector, limit=limit))


@mcp.tool()
def list_tools() -> str:
    """List every tool and action Show2Flow currently exposes."""
    return json.dumps(_registry.describe())


if __name__ == "__main__":
    mcp.run()
