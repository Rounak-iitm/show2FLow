"""Tracks the state of a single workflow run, so it can be persisted
by the recorder and inspected/replayed later."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StepResult:
    step_id: str
    tool: str
    action: str
    status: str  # "success" | "failed" | "healed"
    started_at: float
    finished_at: float
    output: Any = None
    error: Optional[str] = None
    healed_from: Optional[Dict[str, Any]] = None  # original args if healed
    healed_to: Optional[Dict[str, Any]] = None     # replacement args if healed
    healer_confidence: Optional[float] = None

    def duration(self) -> float:
        return self.finished_at - self.started_at

    def to_dict(self) -> Dict[str, Any]:
        d = self.__dict__.copy()
        d["duration_seconds"] = round(self.duration(), 4)
        return d


@dataclass
class RunState:
    workflow_name: str
    run_id: str
    started_at: float = field(default_factory=time.time)
    finished_at: Optional[float] = None
    step_results: List[StepResult] = field(default_factory=list)

    def add(self, result: StepResult) -> None:
        self.step_results.append(result)

    def finish(self) -> None:
        self.finished_at = time.time()

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.step_results if r.status == "success")

    @property
    def healed_count(self) -> int:
        return sum(1 for r in self.step_results if r.status == "healed")

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.step_results if r.status == "failed")

    def summary(self) -> Dict[str, Any]:
        return {
            "workflow_name": self.workflow_name,
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": round((self.finished_at or time.time()) - self.started_at, 4),
            "total_steps": len(self.step_results),
            "success": self.success_count,
            "healed": self.healed_count,
            "failed": self.failed_count,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            **self.summary(),
            "steps": [r.to_dict() for r in self.step_results],
        }
