"""Verifier: decides whether a step's output actually satisfies its
`expect` clause, not just whether it raised no exception. A step that
"succeeds" but extracts an empty list, for instance, should not be
treated as a real success.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple


def verify(output: Any, expect: Optional[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    if expect is None:
        return True, None

    expected_type = expect.get("type")
    if expected_type == "list":
        if not isinstance(output, list):
            return False, f"expected a list, got {type(output).__name__}"
        min_items = expect.get("min_items")
        if min_items is not None and len(output) < min_items:
            return False, f"expected >= {min_items} items, got {len(output)}"

    elif expected_type == "dict":
        if not isinstance(output, dict):
            return False, f"expected a dict, got {type(output).__name__}"
        required_keys = expect.get("required_keys", [])
        missing = [k for k in required_keys if k not in output]
        if missing:
            return False, f"missing required keys: {missing}"

    elif expected_type == "nonempty_str":
        if not isinstance(output, str) or not output.strip():
            return False, "expected a non-empty string"

    return True, None
