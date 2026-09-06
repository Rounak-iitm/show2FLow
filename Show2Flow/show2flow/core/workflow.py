"""Workflow schema.

A Workflow is a declarative list of Steps. Each Step names a tool
("browser", "files", "documents") and an action on that tool, plus
the arguments for that action and an optional target description used
by the semantic healer if the literal selector/action fails.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkflowStep(BaseModel):
    id: str
    tool: str = Field(..., description="Registered tool name, e.g. 'browser', 'files'")
    action: str = Field(..., description="Action/method name on the tool")
    args: Dict[str, Any] = Field(default_factory=dict)
    # Human-readable description of *intent*, used by the healer to find a
    # semantic replacement when the literal args (e.g. a selector or exact
    # button text) no longer match the live page.
    target_description: Optional[str] = None
    # Optional JSON-schema-ish expectation used by the verifier to decide
    # whether the step actually succeeded (beyond "no exception raised").
    expect: Optional[Dict[str, Any]] = None


class Workflow(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStep]

    def step_by_id(self, step_id: str) -> WorkflowStep:
        for s in self.steps:
            if s.id == step_id:
                return s
        raise KeyError(f"No step with id {step_id!r}")
