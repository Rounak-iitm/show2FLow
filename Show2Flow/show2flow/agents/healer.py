
from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import List, Optional

from show2flow.tools.browser import BrowserTool


@dataclass
class HealResult:
    matched: bool
    selector: Optional[str] = None
    matched_text: Optional[str] = None
    confidence: float = 0.0
    backend: str = "difflib"


_embedder = None


def _try_load_embedder():
    global _embedder
    if _embedder is not None:
        return _embedder
    try:
        from sentence_transformers import SentenceTransformer

        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        _embedder = False  # sentinel: unavailable, don't retry every call
    return _embedder


def _difflib_best_match(target: str, candidates: List[dict]) -> HealResult:
    if not candidates:
        return HealResult(matched=False, backend="difflib")
    scored = [
        (difflib.SequenceMatcher(None, target.lower(), c["text"].lower()).ratio(), c)
        for c in candidates
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best = scored[0]
    return HealResult(
        matched=best_score >= 0.35,
        selector=best["selector"],
        matched_text=best["text"],
        confidence=round(best_score, 4),
        backend="difflib",
    )


def _embedding_best_match(target: str, candidates: List[dict]) -> HealResult:
    embedder = _try_load_embedder()
    if not embedder or not candidates:
        return HealResult(matched=False, backend="embedding")

    import numpy as np

    texts = [c["text"] for c in candidates]
    target_vec = embedder.encode([target])[0]
    cand_vecs = embedder.encode(texts)
    sims = cand_vecs @ target_vec / (
        (cand_vecs**2).sum(axis=1) ** 0.5 * (target_vec**2).sum() ** 0.5 + 1e-9
    )
    best_idx = int(np.argmax(sims))
    best_score = float(sims[best_idx])
    return HealResult(
        matched=best_score >= 0.45,
        selector=candidates[best_idx]["selector"],
        matched_text=candidates[best_idx]["text"],
        confidence=round(best_score, 4),
        backend="embedding",
    )


def heal(
    browser: BrowserTool,
    target_description: str,
    prefer_embedding: bool = True,
) -> HealResult:
    """Look at the live page and try to find a replacement element for a
    failed step, based on target_description."""
    candidates = browser.candidate_elements(kind="clickable")

    if prefer_embedding:
        result = _embedding_best_match(target_description, candidates)
        if result.matched:
            return result

    return _difflib_best_match(target_description, candidates)
