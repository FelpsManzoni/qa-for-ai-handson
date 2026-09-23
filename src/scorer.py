"""The LLM-eval system's scoring engine.

score_pair() is the one function every mode (online/offline) calls. It is
deliberately deterministic: no LLM is asked to judge anything here (see
docs/01_overview.md for why). This file is what gets built live, in two
increments:

  Increment 1 (checkpoint-1): token_f1 + keypoint_coverage for one example
  Increment 2 (checkpoint-2): + semantic_similarity, full JSON contract

TODO(checkpoint-1): implement token_f1() and keypoint_coverage()
TODO(checkpoint-2): implement semantic_similarity() and wire it into score_pair()
"""
from __future__ import annotations

import re
from typing import Optional

# --- Config: change weights/threshold here, not scattered through the codebase ---
WEIGHTS = {"token_f1": 0.4, "keypoint_coverage": 0.3, "semantic_similarity": 0.3}
THRESHOLD = 0.70


def _normalize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split into tokens."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return [t for t in text.split() if t]


def token_f1(reference: str, candidate: str) -> float:
    """TODO(checkpoint-1): SQuAD-style token-overlap F1 between two texts."""
    raise NotImplementedError("Implement token_f1 in checkpoint-1")


def keypoint_coverage(key_points: list[str], candidate: str) -> float:
    """TODO(checkpoint-1): fraction of key_points found in candidate (normalized substring match)."""
    raise NotImplementedError("Implement keypoint_coverage in checkpoint-1")


def semantic_similarity(reference: str, candidate: str) -> Optional[float]:
    """TODO(checkpoint-2): cosine similarity between local sentence embeddings.
    Returns None if the embedding backend isn't available (see src/embeddings.py)."""
    raise NotImplementedError("Implement semantic_similarity in checkpoint-2")


def score_pair(
    question: str,
    reference_answer: str,
    key_points: list[str],
    model_answer: str,
    mode: str = "offline",
    latency_ms: Optional[float] = None,
) -> dict:
    """Placeholder until checkpoint-2. Returns a fixed, obviously-fake result so
    the pipeline plumbing (runners, CLI, analyze.py) can be exercised end to end
    before any scoring logic exists."""
    return {
        "token_f1": None,
        "keypoint_coverage": None,
        "semantic_similarity": None,
        "overall": None,
        "pass": None,
        "mode": mode,
        "latency_ms": latency_ms,
        "note": "scorer not implemented yet — see checkpoint-1 and checkpoint-2",
    }
