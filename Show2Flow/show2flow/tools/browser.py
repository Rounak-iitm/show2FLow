"""Deterministic browser control via Playwright.

Kept as a thin wrapper: every method takes plain JSON-serializable args
(so it can be driven straight from a workflow YAML file or from an MCP
tool call) and returns plain JSON-serializable output.

Playwright is imported lazily so the rest of Show2Flow (recorder,
workflow schema, tests) works even before `playwright install` has been
run.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class BrowserTool:
    def __init__(self, headless: bool = True) -> None:
        self.headless = headless
        self._playwright = None
        self._browser = None
        self._page = None

    # -- lifecycle -----------------------------------------------------
    def _ensure_started(self) -> None:
        if self._page is not None:
            return
        from playwright.sync_api import sync_playwright

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        self._page = self._browser.new_page()

    def close(self) -> None:
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        self._browser = None
        self._page = None
        self._playwright = None

    # -- actions used directly from workflow steps ----------------------
    def open(self, url: str, timeout_ms: int = 15000) -> Dict[str, Any]:
        self._ensure_started()
        self._page.goto(url, timeout=timeout_ms)
        return {"url": self._page.url, "title": self._page.title()}

    def click(self, selector: str, timeout_ms: int = 5000) -> Dict[str, Any]:
        self._ensure_started()
        self._page.click(selector, timeout=timeout_ms)
        return {"clicked": selector}

    def fill(self, selector: str, text: str, timeout_ms: int = 5000) -> Dict[str, Any]:
        self._ensure_started()
        self._page.fill(selector, text, timeout=timeout_ms)
        return {"filled": selector, "text": text}

    def press(self, selector: str, key: str, timeout_ms: int = 5000) -> Dict[str, Any]:
        self._ensure_started()
        self._page.press(selector, key, timeout=timeout_ms)
        return {"selector": selector, "key": key}

    def extract(
        self, selector: str, attr: Optional[str] = None, limit: int = 20
    ) -> List[str]:
        """Extract text (or an attribute) from every element matching selector."""
        self._ensure_started()
        handles = self._page.query_selector_all(selector)
        out: List[str] = []
        for h in handles[:limit]:
            out.append(h.get_attribute(attr) if attr else (h.inner_text() or "").strip())
        return out

    def screenshot(self, path: str) -> Dict[str, Any]:
        self._ensure_started()
        self._page.screenshot(path=path)
        return {"screenshot": path}

    # -- used by the healer to find a semantic replacement --------------
    def candidate_elements(self, kind: str = "clickable", limit: int = 200) -> List[Dict[str, str]]:
        """Return {text, selector} for elements the healer can match
        against a failed step's target_description."""
        self._ensure_started()
        css = "a, button, input, [role=button], [onclick]" if kind == "clickable" else "*"
        handles = self._page.query_selector_all(css)
        candidates = []
        for i, h in enumerate(handles[:limit]):
            text = (h.inner_text() or h.get_attribute("value") or h.get_attribute("aria-label") or "").strip()
            if not text:
                continue
            tag = h.evaluate("el => el.tagName.toLowerCase()")
            candidates.append({"text": text, "selector": f"{tag} >> nth={i}", "tag": tag})
        return candidates
