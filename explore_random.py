"""Try fresh random review draws without changing the official C1 evaluation."""

from __future__ import annotations

import argparse
import json
import secrets
from pathlib import Path

import numpy as np

from experiment import evaluate_top_k, inject_noise, read_idx, split_train_indices


ROOT = Path(__file__).resolve().parent
TRAIN_LABELS = ROOT / "data" / "raw" / "train-labels-idx1-ubyte.gz"


def draw_random_trials(error_type: np.ndarray, budget: int, runs: int, seed: int) -> list[dict]:
    """Draw `runs` independent, reproducible random review queues."""
    if runs < 1:
        raise ValueError("runs must be positive")
    if not 1 <= budget <= len(error_type):
        raise ValueError("budget must be between 1 and the number of rows")
    trials = []
    for offset in range(runs):
        selected = np.random.default_rng(seed + offset).permutation(len(error_type))[:budget]
        metric = evaluate_top_k(selected, error_type, budget)
        trials.append({
            "seed": seed + offset,
            "selected_rows": selected.tolist(),
            "errors_found": metric["errors_found"],
            "error_recall": metric["error_recall"],
        })
    return trials


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=100, help="Number of fresh random draws; default 100")
    parser.add_argument("--seed", type=int, help="Repeatable first seed; omit for a fresh seed on each invocation")
    args = parser.parse_args()

    labels = read_idx(TRAIN_LABELS)
    _, eval_ids = split_train_indices(labels, seed=20260924)
    _, error_type, _ = inject_noise(labels[eval_ids], seed=677)
    budget = int(np.ceil(0.05 * len(eval_ids)))
    first_seed = args.seed if args.seed is not None else secrets.randbits(32)
    trials = draw_random_trials(error_type, budget, args.runs, first_seed)
    counts = [trial["errors_found"] for trial in trials]
    print(json.dumps({
        "purpose": "Exploration only; the official 100-seed baseline in results.json stays unchanged.",
        "first_seed": first_seed,
        "runs": args.runs,
        "first_ten_errors_found": counts[:10],
        "first_draw_image_ids": eval_ids[trials[0]["selected_rows"][:10]].tolist(),
        "mean_errors_found": float(np.mean(counts)),
        "min_errors_found": min(counts),
        "max_errors_found": max(counts),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
