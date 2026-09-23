"""Online mode: model_answer is produced live by calling an LLM via OpenRouter.
Post-session improvement ("Continue daqui 2" in docs/07_opencode_build_guide.md) — needs OPENROUTER_API_KEY in .env.

TODO(checkpoint-4): implement call_model() and run_online()
"""
from __future__ import annotations

import csv
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

from src.scorer import score_pair

DATASET_PATH = Path("data/golden_dataset.csv")
RESULTS_PATH = Path("data/results.csv")

load_dotenv()


def call_model(question: str) -> dict:
    """TODO(checkpoint-4): POST to OpenRouter's chat completions endpoint with
    `question` as the single user message. Return a dict with:
      - answer: str (the model's reply text)
      - latency_ms: float
      - status: "ok" | "error"
      - error_detail: str | None
    A failing call must be caught and returned as status="error", never raised,
    so one bad request doesn't stop the whole batch.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    model = os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
    base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    if not api_key:
        return {"answer": "", "latency_ms": None, "status": "error",
                 "error_detail": "OPENROUTER_API_KEY not set in .env"}

    start = time.perf_counter()
    try:
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "messages": [{"role": "user", "content": question}]},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        answer = data["choices"][0]["message"]["content"]
        latency_ms = (time.perf_counter() - start) * 1000
        return {"answer": answer, "latency_ms": latency_ms, "status": "ok", "error_detail": None}
    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        return {"answer": "", "latency_ms": latency_ms, "status": "error", "error_detail": str(exc)}


def run_online(dataset_path: Path = DATASET_PATH, results_path: Path = RESULTS_PATH) -> list[dict]:
    """TODO(checkpoint-4): for each row in dataset_path, call_model(question) to
    get a live answer, then score_pair() the same way offline_runner does, and
    write results_path. A failed call still produces a row (overall=None,
    status="error") rather than aborting the batch."""
    rows = []
    with dataset_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            call = call_model(row["question"])
            if call["status"] == "ok":
                key_points = [kp.strip() for kp in row["key_points"].split(";") if kp.strip()]
                try:
                    result = score_pair(
                        question=row["question"],
                        reference_answer=row["reference_answer"],
                        key_points=key_points,
                        model_answer=call["answer"],
                        mode="online",
                        latency_ms=call["latency_ms"],
                    )
                except Exception as exc:
                    result = {"overall": None, "pass": None, "error": str(exc)}
            else:
                result = {
                    "overall": None, "pass": None, "mode": "online",
                    "latency_ms": call["latency_ms"], "error": call["error_detail"],
                }
            result["id"] = row["id"]
            rows.append(result)

    if rows:
        fieldnames = ["id"] + sorted({k for r in rows for k in r.keys() if k != "id"})
        with results_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    return rows


if __name__ == "__main__":
    results = run_online()
    ok = sum(1 for r in results if r.get("overall") is not None)
    print(f"Wrote {len(results)} rows to {RESULTS_PATH} ({ok} scored successfully)")
