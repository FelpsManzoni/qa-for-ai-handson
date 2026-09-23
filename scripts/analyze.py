#!/usr/bin/env python3
"""Analysis script for the closing discussion block. Loads data/results.csv,
prints the headline metrics, and saves a histogram of overall scores.

Run after scripts/evaluate.py. Optional argument: a results CSV path
(default data/results.csv), e.g. `python scripts/analyze.py data/results_2sinais.csv`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RESULTS_PATH = Path("data/results.csv")
CHART_PATH = Path("data/score_distribution.png")
THRESHOLD_DEFAULT = 0.70


def main():
    results_path = Path(sys.argv[1]) if len(sys.argv) > 1 else RESULTS_PATH
    chart_path = (CHART_PATH if results_path == RESULTS_PATH
                  else results_path.with_name(f"{results_path.stem}_distribution.png"))

    if not results_path.exists():
        print(f"No {results_path} found yet — run scripts/evaluate.py first.")
        sys.exit(1)

    df = pd.read_csv(results_path)
    scored = df.dropna(subset=["overall"]) if "overall" in df.columns else df.iloc[0:0]

    print(f"Loaded {len(df)} rows ({len(scored)} scored, {len(df) - len(scored)} unscored/errored).")

    if scored.empty:
        print("Nothing scored yet — the scorer hasn't been implemented, or every call failed.")
        print("This is expected right after checkpoint-0; come back once checkpoint-2+ is done.")
        return

    print(f"\nMean overall:   {scored['overall'].mean():.2f}")
    print(f"Median overall: {scored['overall'].median():.2f}")
    if "pass" in scored.columns:
        pass_rate = scored["pass"].astype(bool).mean()
        print(f"Pass rate:      {pass_rate:.0%}")

    print("\nPer-signal means:")
    for col in ["token_f1", "keypoint_coverage", "semantic_similarity"]:
        if col in scored.columns and scored[col].notna().any():
            print(f"  {col:<20} {scored[col].mean():.2f}")

    if "latency_ms" in scored.columns and scored["latency_ms"].notna().any():
        print(f"\nMean latency (online only): {scored['latency_ms'].mean():.0f} ms")

    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 4))
        scored["overall"].plot(kind="hist", bins=10, ax=ax, edgecolor="white")
        ax.axvline(THRESHOLD_DEFAULT, linestyle="--", label=f"threshold ({THRESHOLD_DEFAULT})")
        ax.set_xlabel("overall score")
        ax.set_title("Distribution of overall scores")
        ax.legend()
        fig.tight_layout()
        fig.savefig(chart_path, dpi=150)
        print(f"\nSaved distribution chart to {chart_path}")
    except Exception as exc:
        print(f"\n(Skipped chart: {exc})")


if __name__ == "__main__":
    main()
