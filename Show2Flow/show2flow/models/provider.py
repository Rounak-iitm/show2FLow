"""Model backend abstraction.

Keeps every model call behind one interface so:
  - the intent parser (Phase 2) can move from regex to an LLM call
  - the healer can move from difflib to embeddings (already supported,
    see agents/healer.py) or to a locally-hosted instruction model

without other modules caring which backend is active. Matches the
Hugging Face/PyTorch workflow already used in the LoRA project, so the
same environment can serve both.
"""
from __future__ import annotations

from typing import List, Optional


class ModelProvider:
    """Base interface. Subclass this for each backend."""

    def generate(self, prompt: str, max_new_tokens: int = 256) -> str:
        raise NotImplementedError

    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError


class HuggingFaceProvider(ModelProvider):
    """Thin wrapper around a local `transformers` text-generation
    pipeline. Lazily imported so Show2Flow works before `transformers`
    is installed (Phase 1/2 don't need it at all).
    """

    def __init__(self, model_name: str = "Qwen/Qwen2.5-0.5B-Instruct", device: Optional[str] = None):
        self.model_name = model_name
        self.device = device
        self._pipe = None

    def _ensure_loaded(self):
        if self._pipe is not None:
            return
        from transformers import pipeline

        self._pipe = pipeline(
            "text-generation",
            model=self.model_name,
            device=self.device,
        )

    def generate(self, prompt: str, max_new_tokens: int = 256) -> str:
        self._ensure_loaded()
        out = self._pipe(prompt, max_new_tokens=max_new_tokens, do_sample=False)
        return out[0]["generated_text"]


class NullProvider(ModelProvider):
    """No-op provider used when no model backend is configured. Lets the
    rule-based intent parser / difflib healer run standalone."""

    def generate(self, prompt: str, max_new_tokens: int = 256) -> str:
        raise RuntimeError(
            "No model provider configured. Pass a HuggingFaceProvider, or keep "
            "using the rule-based agents (intent.py / healer.py's difflib path)."
        )

    def embed(self, texts: List[str]) -> List[List[float]]:
        raise RuntimeError("No model provider configured.")
