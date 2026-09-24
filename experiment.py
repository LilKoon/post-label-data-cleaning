"""Small, reproducible C1 experiment on Fashion-MNIST (NumPy only)."""

from __future__ import annotations

import gzip
import struct
from pathlib import Path

import numpy as np


CLASS_NAMES = (
    "T-shirt/top", "Trouser", "Pullover", "Dress", "Coat",
    "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot",
)
ERROR_NAMES = {1: "random", 2: "systematic", 3: "batch"}


def read_idx(path: Path) -> np.ndarray:
    """Read IDX images or labels from the official gzip files."""
    with gzip.open(path, "rb") as handle:
        header = handle.read(4)
        if len(header) != 4 or header[:3] != b"\x00\x00\x08":
            raise ValueError(f"Invalid unsigned-byte IDX file: {path}")
        dimensions = header[3]
        if dimensions not in (1, 3):
            raise ValueError(f"Unexpected IDX dimension count: {dimensions}")
        shape_bytes = handle.read(4 * dimensions)
        shape = struct.unpack(">" + "I" * dimensions, shape_bytes)
        data = np.frombuffer(handle.read(), dtype=np.uint8)
    if data.size != int(np.prod(shape)):
        raise ValueError(f"IDX length does not match header: {path}")
    return data.reshape(shape).copy()


def split_train_indices(labels: np.ndarray, seed: int = 20260924) -> tuple[np.ndarray, np.ndarray]:
    """Choose 800 development and 200 evaluation examples per class."""
    rng = np.random.default_rng(seed)
    dev, evaluation = [], []
    for class_id in range(10):
        choices = rng.permutation(np.flatnonzero(labels == class_id))[:1000]
        if len(choices) != 1000:
            raise ValueError(f"Not enough examples for class {class_id}")
        dev.extend(choices[:800])
        evaluation.extend(choices[800:])
    return rng.permutation(np.asarray(dev)), rng.permutation(np.asarray(evaluation))


def test_indices(labels: np.ndarray, seed: int = 20260924) -> np.ndarray:
    rng = np.random.default_rng(seed + 1)
    chosen = []
    for class_id in range(10):
        values = rng.permutation(np.flatnonzero(labels == class_id))[:200]
        if len(values) != 200:
            raise ValueError(f"Not enough test examples for class {class_id}")
        chosen.extend(values)
    return rng.permutation(np.asarray(chosen))


def inject_noise(
    original: np.ndarray, seed: int, rate: float = 0.10, batch_size: int = 20
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Inject three disjoint label-error mechanisms into a copy of labels.

    Error types: 1 random flip, 2 Shirt -> T-shirt/top, 3 entire batch +1.
    Batch IDs are assigned before corruption. Rate is exact for the rates used
    in this experiment: 5%, 10%, and 20%.
    """
    if not 0 < rate < 1:
        raise ValueError("rate must be between zero and one")
    labels = np.asarray(original, dtype=np.uint8)
    n = len(labels)
    rng = np.random.default_rng(seed)
    permutation = rng.permutation(n)
    batch_id = np.empty(n, dtype=np.int32)
    batch_id[permutation] = np.arange(n) // batch_size
    noisy = labels.copy()
    error_type = np.zeros(n, dtype=np.uint8)

    batch_count = int(round(n * rate * 0.20 / batch_size))
    batch_rows = permutation[: batch_count * batch_size]
    noisy[batch_rows] = (labels[batch_rows] + 1) % 10
    error_type[batch_rows] = 3

    systematic_count = int(round(n * rate * 0.40))
    eligible = np.flatnonzero((labels == 6) & (error_type == 0))
    if len(eligible) < systematic_count:
        raise ValueError("Not enough Shirt examples for systematic errors")
    systematic_rows = rng.choice(eligible, size=systematic_count, replace=False)
    noisy[systematic_rows] = 0
    error_type[systematic_rows] = 2

    random_count = int(round(n * rate * 0.40))
    eligible = np.flatnonzero(error_type == 0)
    random_rows = rng.choice(eligible, size=random_count, replace=False)
    noisy[random_rows] = (labels[random_rows] + rng.integers(1, 10, size=random_count)) % 10
    error_type[random_rows] = 1
    return noisy, error_type, batch_id


def image_features(images: np.ndarray) -> np.ndarray:
    """Average each 2x2 pixel block, giving a 14x14 feature vector."""
    if images.ndim != 3 or images.shape[1:] != (28, 28):
        raise ValueError("Expected N x 28 x 28 images")
    return (images.reshape(-1, 14, 2, 14, 2).mean(axis=(2, 4)) / 255).reshape(-1, 196).astype(np.float32)


def neighbor_probabilities(
    train_features: np.ndarray,
    train_labels: np.ndarray,
    query_features: np.ndarray,
    neighbors: int = 15,
    chunk_size: int = 128,
) -> np.ndarray:
    """Class votes of nearest images, weighted by inverse pixel distance."""
    if neighbors < 1 or neighbors > len(train_features):
        raise ValueError("Invalid neighbor count")
    train = np.asarray(train_features, dtype=np.float32)
    query = np.asarray(query_features, dtype=np.float32)
    train_norm = np.sum(train * train, axis=1)
    output = np.empty((len(query), 10), dtype=np.float32)
    for start in range(0, len(query), chunk_size):
        block = query[start : start + chunk_size]
        distances = np.sum(block * block, axis=1)[:, None] + train_norm[None, :] - 2 * block @ train.T
        nearest = np.argpartition(distances, neighbors - 1, axis=1)[:, :neighbors]
        nearest_distance = np.maximum(np.take_along_axis(distances, nearest, axis=1), 0)
        weights = 1 / (np.sqrt(nearest_distance) + 0.05)
        votes = np.zeros((len(block), 10), dtype=np.float32)
        np.add.at(votes, (np.arange(len(block))[:, None], train_labels[nearest]), weights)
        output[start : start + len(block)] = votes / np.sum(votes, axis=1, keepdims=True)
    return output


def rank_suspicion(scores: np.ndarray) -> np.ndarray:
    """Highest suspicion first; original row order breaks score ties."""
    scores = np.asarray(scores)
    return np.lexsort((np.arange(len(scores)), -scores))


def evaluate_top_k(ranking: np.ndarray, error_type: np.ndarray, budget_count: int) -> dict:
    errors = np.asarray(error_type)
    selected = np.asarray(ranking)[:budget_count]
    if len(selected) != budget_count or len(np.unique(selected)) != budget_count:
        raise ValueError("Ranking does not contain the requested unique rows")
    if np.any(selected < 0) or np.any(selected >= len(errors)):
        raise ValueError("Ranking contains an out-of-range row")
    total = int(np.count_nonzero(errors))
    found = int(np.count_nonzero(errors[selected]))
    found_by_type = {name: int(np.count_nonzero(errors[selected] == code)) for code, name in ERROR_NAMES.items()}
    total_by_type = {name: int(np.count_nonzero(errors == code)) for code, name in ERROR_NAMES.items()}
    return {
        "reviewed": int(budget_count),
        "errors_found": found,
        "total_errors": total,
        "error_recall": found / total if total else 0.0,
        "precision": found / budget_count if budget_count else 0.0,
        "found_by_type": found_by_type,
        "total_by_type": total_by_type,
    }
