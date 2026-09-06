"""File tool: the persistence sink most demo workflows write results to."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class FileTool:
    def save_json(self, path: str, data: Any) -> Dict[str, Any]:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        return {"saved": str(p), "bytes": p.stat().st_size}

    def save_text(self, path: str, text: str) -> Dict[str, Any]:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return {"saved": str(p), "bytes": p.stat().st_size}

    def read_json(self, path: str) -> Any:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_files(self, directory: str, pattern: str = "*") -> list[str]:
        return [str(p) for p in Path(directory).glob(pattern)]
