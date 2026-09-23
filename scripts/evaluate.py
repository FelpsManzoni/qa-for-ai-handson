#!/usr/bin/env python3
"""CLI entrypoint for the LLM-eval system.

Usage:
    python scripts/evaluate.py --mode offline
    python scripts/evaluate.py --mode online
    python scripts/evaluate.py --mode offline --no-semantic --out data/results_2sinais.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as `python scripts/evaluate.py` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import scorer  # noqa: E402
from src.offline_runner import run_offline  # noqa: E402
from src.online_runner import run_online  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Run the LLM-eval system.")
    parser.add_argument("--mode", choices=["offline", "online"], default="offline")
    parser.add_argument("--dataset", default="data/golden_dataset.csv")
    parser.add_argument("--out", default="data/results.csv")
    parser.add_argument("--threshold", type=float, default=None,
                         help="Override scorer.THRESHOLD for this run.")
    parser.add_argument("--no-semantic", action="store_true",
                        help="Disable the semantic-similarity signal for this run "
                             "(simulates an unavailable embedding backend).")
    args = parser.parse_args()

    if args.no_semantic:
        import src.embeddings as embeddings

        def _no_embedder():
            return None

        embeddings.get_embedder = _no_embedder
        scorer.get_embedder = _no_embedder  # in case scorer imported it at module level

    if args.threshold is not None:
        scorer.THRESHOLD = args.threshold

    dataset_path = Path(args.dataset)
    results_path = Path(args.out)

    if args.mode == "offline":
        results = run_offline(dataset_path, results_path)
    else:
        results = run_online(dataset_path, results_path)

    scored = [r for r in results if r.get("overall") is not None]
    print(f"[{args.mode}] {len(results)} rows processed, {len(scored)} scored, results -> {results_path}")


if __name__ == "__main__":
    main()
