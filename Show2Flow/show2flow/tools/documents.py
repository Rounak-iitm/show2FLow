"""Document tool. Placeholder for the Unstructured-backed pipeline
described in Phase 3 (PDF -> Unstructured -> elements -> Show2Flow).

For now this exposes a minimal, dependency-light PDF text extractor
(pypdf, if installed) so document workflows can be prototyped before
Unstructured is added.
"""
from __future__ import annotations

from typing import Any, Dict, List


class DocumentTool:
    def extract_text(self, path: str) -> Dict[str, Any]:
        try:
            from pypdf import PdfReader
        except ImportError as e:
            raise RuntimeError(
                "pypdf is not installed. Run `pip install pypdf`, or wait for the "
                "Phase-3 Unstructured-backed document pipeline."
            ) from e

        reader = PdfReader(path)
        pages: List[str] = [page.extract_text() or "" for page in reader.pages]
        return {"path": path, "num_pages": len(pages), "text": "\n".join(pages)}

    def extract_elements(self, path: str) -> Any:
        """Reserved for the Unstructured-based pipeline (Phase 3)."""
        raise NotImplementedError(
            "extract_elements() will use the 'unstructured' library once it is "
            "added in Phase 3 (see README)."
        )
