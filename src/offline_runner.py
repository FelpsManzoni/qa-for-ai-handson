"""Offline mode: model_answer already exists in the golden dataset (pre-run by a
known model ahead of time), so this needs no network access at all.

TODO(checkpoint-3): finish run_offline() so it writes a complete data/results.csv
"""
from __future__ import annotations

import csv
from pathlib import Path

from src.scorer import score_pair

DATASET_PATH = Path("data/golden_dataset.csv")
RESULTS_PATH = Path("data/results.csv")


def run_offline(dataset_path: Path = DATASET_PATH, results_path: Path = RESULTS_PATH) -> list[dict]:
    """TODO(checkpoint-3): read dataset_path, call score_pair() per row using the
    model_answer_offline column, write results_path, return the list of result rows.

    Checkpoint-0 behavior: reads the dataset and calls the (not-yet-implemented)
    scorer so the CLI and file plumbing can be verified before any scoring logic
    exists. Every row will carry the scorer's placeholder output until
    checkpoint-1/2 are done.
    """
    rows = []
    with dataset_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                key_points = [kp.strip() for kp in row["key_points"].split(";") if kp.strip()]
                result = score_pair(
                    question=row["question"],
                    reference_answer=row["reference_answer"],
                    key_points=key_points,
                    model_answer=row["model_answer_offline"],
                    mode="offline",
                )
            except Exception as exc:  # a single bad row must not lose the rest
                result = {"overall": None, "pass": None, "error": str(exc)}
            result["id"] = row["id"]
            rows.append(result)

    if rows:
        fieldnames = ["id"] + [k for k in rows[0].keys() if k != "id"]
        with results_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    return rows


if __name__ == "__main__":
    results = run_offline()
    print(f"Wrote {len(results)} rows to {RESULTS_PATH}")
