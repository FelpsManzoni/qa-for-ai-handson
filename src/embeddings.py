"""Local sentence-embedding helper for the semantic-similarity signal.

This is intentionally NOT part of what gets built live during the session — it's
infrastructure the scorer depends on optionally. If the embedding library isn't
available, get_embedder() returns None and scorer.py falls back to the two
remaining signals (see docs/02_architecture.md).
"""
from __future__ import annotations

import math
from functools import lru_cache
from typing import Optional, Sequence

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class Embedder:
    """Thin wrapper around fastembed so the rest of the codebase doesn't
    need to know which embedding library is in use."""

    def __init__(self, model_name: str = _MODEL_NAME):
        from fastembed import TextEmbedding  # imported lazily, may not be installed

        self._model = TextEmbedding(model_name=model_name)

    def encode(self, text: str) -> Sequence[float]:
        # fastembed's .embed() returns a generator of numpy arrays
        return next(iter(self._model.embed([text])))

    @staticmethod
    def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


@lru_cache(maxsize=1)
def get_embedder() -> Optional[Embedder]:
    """Returns a cached Embedder instance, or None if the dependency (or the
    model download, if the machine is offline) isn't available.

    Cached so we only pay the model-load cost once per process, not once per
    example scored.
    """
    try:
        return Embedder()
    except Exception:
        return None
