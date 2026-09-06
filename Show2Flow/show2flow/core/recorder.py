"""Persistence layer. No database — workflows are YAML files under
workflows/, and completed runs are JSON files under runs/.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Optional

import yaml

from show2flow.core.workflow import Workflow
from show2flow.core.state import RunState

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS_DIR = REPO_ROOT / "workflows"
RUNS_DIR = REPO_ROOT / "runs"
RECORDINGS_DIR = REPO_ROOT / "recordings"


def load_workflow(path: str | Path) -> Workflow:
    path = Path(path)
    if not path.is_absolute() and not path.exists():
        # allow "search_jobs.yaml" or "examples/search_jobs.yaml"
        candidate = WORKFLOWS_DIR / path
        if candidate.exists():
            path = candidate
        else:
            candidate = WORKFLOWS_DIR / "examples" / path
            if candidate.exists():
                path = candidate
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return Workflow(**raw)


def save_workflow(workflow: Workflow, path: Optional[str | Path] = None) -> Path:
    if path is None:
        path = WORKFLOWS_DIR / "examples" / f"{workflow.name}.yaml"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(json.loads(workflow.model_dump_json()), f, sort_keys=False)
    return path


def new_run_id() -> str:
    return uuid.uuid4().hex[:12]


def save_run(state: RunState) -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RUNS_DIR / f"{state.workflow_name}_{state.run_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, indent=2, default=str)
    return out_path


def list_runs():
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(RUNS_DIR.glob("*.json"))
