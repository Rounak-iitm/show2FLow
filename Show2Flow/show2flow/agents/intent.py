
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Intent:
    action: str  # "search_and_extract" | "unknown"
    url: Optional[str] = None
    query: Optional[str] = None
    result_limit: int = 5
    save_path: Optional[str] = None
    raw_text: str = ""
    notes: List[str] = field(default_factory=list)


_URL_RE = re.compile(r"https?://\S+")
_LIMIT_RE = re.compile(r"first (\d+)")


def parse(task_text: str, default_url: Optional[str] = None) -> Intent:
    text = task_text.strip()
    lower = text.lower()

    url_match = _URL_RE.search(text)
    url = url_match.group(0) if url_match else default_url

    limit_match = _LIMIT_RE.search(lower)
    limit = int(limit_match.group(1)) if limit_match else 5

    if "search" in lower or "find" in lower:
        # crude query extraction: text between "search for"/"find" and
        # the next comma/period/"and"
        q_match = re.search(r"(?:search for|find)\s+(.*?)(?:,| and |\.|$)", lower)
        query = q_match.group(1).strip() if q_match else None
        return Intent(
            action="search_and_extract",
            url=url,
            query=query,
            result_limit=limit,
            raw_text=text,
        )

    return Intent(action="unknown", url=url, raw_text=text, notes=["Could not classify intent"])
