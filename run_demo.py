"""Run the offline C1 Fashion-MNIST demonstration and write measured results."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from pathlib import Path

import numpy as np

from experiment import (
    CLASS_NAMES,
    evaluate_top_k,
    image_features,
    inject_noise,
    neighbor_probabilities,
    rank_suspicion,
    read_idx,
    split_train_indices,
    test_indices,
)


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
OUTPUT = ROOT / "artifacts"
SPLIT_SEED = 20260924
DEVELOPMENT_NOISE_SEED = 311
EVALUATION_NOISE_SEED = 677
RANDOM_BASELINE_SEEDS = tuple(range(1000, 1100))
BUDGET_FRACTION = 0.05


def source_files() -> dict[str, Path]:
    names = (
        "train-images-idx3-ubyte.gz",
        "train-labels-idx1-ubyte.gz",
        "t10k-images-idx3-ubyte.gz",
        "t10k-labels-idx1-ubyte.gz",
    )
    paths = {name: RAW / name for name in names}
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing Fashion-MNIST source files:\n" + "\n".join(missing))
    return paths


def count_exact_overlap(*image_sets: np.ndarray) -> int:
    hashes = [set(hashlib.sha256(image.tobytes()).digest() for image in images) for images in image_sets]
    return sum(len(hashes[i] & hashes[j]) for i in range(len(hashes)) for j in range(i + 1, len(hashes)))


def write_queue(path: Path, source_ids: np.ndarray, noisy_labels: np.ndarray, probabilities: np.ndarray, ranking: np.ndarray) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("rank", "source_image_id", "current_label", "suggested_label", "suspicion_score"))
        for rank, row in enumerate(ranking[: int(np.ceil(len(ranking) * BUDGET_FRACTION))], start=1):
            writer.writerow((
                rank,
                int(source_ids[row]),
                CLASS_NAMES[int(noisy_labels[row])],
                CLASS_NAMES[int(np.argmax(probabilities[row]))],
                f"{1 - probabilities[row, noisy_labels[row]]:.6f}",
            ))


def run(output_dir: Path = OUTPUT) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    reserved = [output_dir / name for name in ("results.json", "review_queue.csv")]
    existing = [path for path in reserved if path.exists()]
    if existing:
        raise FileExistsError("Choose a new --output-dir; these files already exist: " + ", ".join(map(str, existing)))
    paths = source_files()
    source_hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()}
    train_images = read_idx(paths["train-images-idx3-ubyte.gz"])
    train_labels = read_idx(paths["train-labels-idx1-ubyte.gz"])
    test_images = read_idx(paths["t10k-images-idx3-ubyte.gz"])
    test_labels = read_idx(paths["t10k-labels-idx1-ubyte.gz"])
    dev_ids, eval_ids = split_train_indices(train_labels, SPLIT_SEED)
    heldout_ids = test_indices(test_labels, SPLIT_SEED)
    overlap = count_exact_overlap(train_images[dev_ids], train_images[eval_ids], test_images[heldout_ids])
    if overlap:
        raise ValueError(f"Found {overlap} exact cross-split duplicate image pairs")

    noisy_dev, dev_error_type, _ = inject_noise(train_labels[dev_ids], DEVELOPMENT_NOISE_SEED)
    noisy_eval, eval_error_type, eval_batch_id = inject_noise(train_labels[eval_ids], EVALUATION_NOISE_SEED)
    budget_count = int(np.ceil(len(eval_ids) * BUDGET_FRACTION))

    start = time.perf_counter()
    probabilities = neighbor_probabilities(
        image_features(train_images[dev_ids]), noisy_dev, image_features(train_images[eval_ids])
    )
    score_seconds = time.perf_counter() - start
    scores = 1 - probabilities[np.arange(len(eval_ids)), noisy_eval]
    ranked = rank_suspicion(scores)
    model_result = evaluate_top_k(ranked, eval_error_type, budget_count)

    random_results = []
    for seed in RANDOM_BASELINE_SEEDS:
        random_order = np.random.default_rng(seed).permutation(len(eval_ids))
        random_results.append(evaluate_top_k(random_order, eval_error_type, budget_count))
    random_found = np.array([result["errors_found"] for result in random_results])
    baseline = {
        "runs": len(random_results),
        "mean_errors_found": float(np.mean(random_found)),
        "median_errors_found": float(np.median(random_found)),
        "min_errors_found": int(np.min(random_found)),
        "max_errors_found": int(np.max(random_found)),
        "mean_error_recall": float(np.mean([result["error_recall"] for result in random_results])),
        "mean_precision": float(np.mean([result["precision"] for result in random_results])),
        "mean_found_by_type": {
            name: float(np.mean([result["found_by_type"][name] for result in random_results]))
            for name in model_result["found_by_type"]
        },
    }

    stress_tests = []
    for rate, seed in ((0.05, 678), (0.10, EVALUATION_NOISE_SEED), (0.20, 679)):
        stress_noisy, stress_type, _ = inject_noise(train_labels[eval_ids], seed, rate)
        stress_scores = 1 - probabilities[np.arange(len(eval_ids)), stress_noisy]
        stress_results = evaluate_top_k(rank_suspicion(stress_scores), stress_type, budget_count)
        stress_tests.append({"noise_rate": rate, **stress_results})

    write_queue(output_dir / "review_queue.csv", eval_ids, noisy_eval, probabilities, ranked)
    examples = []
    for row in ranked[:24]:
        examples.append({
            "row": int(row),
            "source_image_id": int(eval_ids[row]),
            "current_label": CLASS_NAMES[int(noisy_eval[row])],
            "suggested_label": CLASS_NAMES[int(np.argmax(probabilities[row]))],
            "reference_label": CLASS_NAMES[int(train_labels[eval_ids[row]])],
            "error_type": {0: "none", 1: "random", 2: "systematic", 3: "batch"}[int(eval_error_type[row])],
            "suspicion_score": float(scores[row]),
            "batch_id": int(eval_batch_id[row]),
        })

    results = {
        "status": "measured",
        "dataset": "Fashion-MNIST (official Zalando Research files)",
        "dataset_url": "https://github.com/zalandoresearch/fashion-mnist",
        "license": "MIT",
        "source_sha256": source_hashes,
        "protocol": {
            "split_seed": SPLIT_SEED,
            "development_noise_seed": DEVELOPMENT_NOISE_SEED,
            "evaluation_noise_seed": EVALUATION_NOISE_SEED,
            "random_baseline_seeds": [RANDOM_BASELINE_SEEDS[0], RANDOM_BASELINE_SEEDS[-1]],
            "development_size": int(len(dev_ids)),
            "evaluation_size": int(len(eval_ids)),
            "downstream_test_reserved": int(len(heldout_ids)),
            "review_budget_fraction": BUDGET_FRACTION,
            "review_budget_count": budget_count,
            "cross_split_exact_duplicate_pairs": overlap,
            "training_errors_by_type": {str(code): int(np.count_nonzero(dev_error_type == code)) for code in (1, 2, 3)},
        },
        "random_baseline": baseline,
        "model": {"name": "15-nearest-neighbor label disagreement (14x14 pixels)", **model_result, "scoring_seconds": score_seconds},
        "stress_tests": stress_tests,
        "top_examples": examples,
        "limitations": [
            "Ground truth is the source dataset label; injected errors are known exactly, natural errors are not exhaustively audited.",
            "Human review time and downstream model recovery have not been measured.",
            "Model flags samples for review; it does not automatically correct labels.",
        ],
    }
    (output_dir / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT, help="New directory for results.json and review_queue.csv")
    report = run(parser.parse_args().output_dir)
    print(json.dumps({"baseline": report["random_baseline"], "model": report["model"], "stress_tests": report["stress_tests"]}, indent=2, ensure_ascii=False))
