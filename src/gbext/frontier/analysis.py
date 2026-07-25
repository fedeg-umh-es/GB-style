"""Post-hoc analysis constrained to simple, auditable frontier predicates."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

import pandas as pd
import yaml


NUMERIC_FEATURES = [
    "max_exponent_ratio",
    "num_exponents_above_half",
    "reduction_density",
    "column_weight_mean",
    "weight",
]
CATEGORICAL_FEATURES = ["coefficient_class"]


def _split_for_k(seed: int, k: int) -> str:
    digest = hashlib.sha256(f"{seed}|holdout|{k}".encode("utf-8")).digest()
    return "holdout" if int.from_bytes(digest[:4], "big") % 3 == 0 else "discovery"


def _balanced_accuracy(labels: list[bool], predictions: list[bool]) -> float:
    positives = [index for index, label in enumerate(labels) if label]
    negatives = [index for index, label in enumerate(labels) if not label]
    if not positives or not negatives:
        return 0.0
    sensitivity = sum(predictions[index] for index in positives) / len(positives)
    specificity = sum(not predictions[index] for index in negatives) / len(negatives)
    return 0.5 * (sensitivity + specificity)


def _crosses_cost_grid(row: pd.Series, rho_grid: list[float]) -> bool:
    signs: set[int] = set()
    for rho in rho_grid:
        delta = float(row["delta_add"]) + rho * float(row["delta_mul_const"])
        signs.add(0 if math.isclose(delta, 0.0, abs_tol=1e-12) else (1 if delta > 0 else -1))
    return -1 in signs and 1 in signs


def _candidate_predicates(discovery: pd.DataFrame) -> list[tuple[str, Callable[[pd.DataFrame], list[bool]]]]:
    predicates: list[tuple[str, Callable[[pd.DataFrame], list[bool]]]] = []
    for feature in NUMERIC_FEATURES:
        values = sorted(set(float(value) for value in discovery[feature].dropna()))
        thresholds = [(left + right) / 2 for left, right in zip(values, values[1:])]
        if len(thresholds) > 64:
            step = max(1, len(thresholds) // 64)
            thresholds = thresholds[::step][:64]
        for threshold in thresholds:
            predicates.append((
                f"{feature} <= {threshold:.12g}",
                lambda frame, f=feature, t=threshold: [float(value) <= t for value in frame[f]],
            ))
            predicates.append((
                f"{feature} > {threshold:.12g}",
                lambda frame, f=feature, t=threshold: [float(value) > t for value in frame[f]],
            ))
    for feature in CATEGORICAL_FEATURES:
        for value in sorted(set(str(item) for item in discovery[feature].dropna())):
            predicates.append((
                f"{feature} == {value!r}",
                lambda frame, f=feature, v=value: [str(item) == v for item in frame[f]],
            ))
    return predicates


def analyze_frontier(config_path: str | Path, parquet_path: str | Path | None = None) -> Path:
    config_path = Path(config_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    output_dir = Path(config["experiment"]["output_dir"])
    parquet_path = Path(parquet_path) if parquet_path else output_dir / "frontier_gate.parquet"
    frame = pd.read_parquet(parquet_path)

    seed = int(config["experiment"]["seed"])
    rho_grid = [float(value) for value in config["cost_model"]["rho_const_grid"]]
    frame = frame.copy()
    frame["crossing"] = frame.apply(lambda row: _crosses_cost_grid(row, rho_grid), axis=1)
    frame["split"] = frame["k"].map(lambda value: _split_for_k(seed, int(value)))

    discovery = frame[frame["split"] == "discovery"]
    holdout = frame[frame["split"] == "holdout"]
    discovery_labels = discovery["crossing"].astype(bool).tolist()
    holdout_labels = holdout["crossing"].astype(bool).tolist()

    best: dict[str, Any] | None = None
    for description, predicate in _candidate_predicates(discovery):
        discovery_predictions = predicate(discovery)
        discovery_score = _balanced_accuracy(discovery_labels, discovery_predictions)
        if best is not None and discovery_score <= best["discovery_balanced_accuracy"]:
            continue
        holdout_predictions = predicate(holdout) if not holdout.empty else []
        holdout_score = _balanced_accuracy(holdout_labels, holdout_predictions) if holdout_predictions else 0.0
        best = {
            "predicate": description,
            "discovery_balanced_accuracy": discovery_score,
            "holdout_balanced_accuracy": holdout_score,
            "discovery_n": len(discovery),
            "holdout_n": len(holdout),
        }

    positives = frame[frame["crossing"]]
    thresholds = config["decision"]
    rule_passes = bool(best) and (
        best["discovery_balanced_accuracy"] >= float(thresholds.get("min_discovery_balanced_accuracy", 0.90))
        and best["holdout_balanced_accuracy"] >= float(thresholds.get("min_holdout_balanced_accuracy", 0.85))
    )
    support_passes = (
        len(positives) >= int(thresholds["min_candidate_instances"])
        and positives["k"].nunique() >= int(thresholds["min_distinct_k"])
        and positives["support"].nunique() >= int(thresholds["min_distinct_supports"])
    )
    status = "PROMOTE_TO_TMVP" if rule_passes and support_passes else "CLOSE_LINE"

    evidence = {
        "status": status,
        "scope": "SEP_SB versus diagnostic FUS_CAN only",
        "crossing_instances": int(len(positives)),
        "crossing_distinct_k": sorted(int(value) for value in positives["k"].unique()),
        "crossing_distinct_supports": int(positives["support"].nunique()),
        "best_simple_rule": best,
        "rule_passes": rule_passes,
        "support_passes": support_passes,
        "mandatory_interpretation": (
            "Proceed only to a source-matched TMVP_REF implementation."
            if status == "PROMOTE_TO_TMVP"
            else "Close the line; do not draft a manuscript."
        ),
    }

    analyzed_path = output_dir / "frontier_gate_analyzed.parquet"
    decision_path = output_dir / "DECISION.md"
    frame.to_parquet(analyzed_path, index=False)
    decision_path.write_text(
        "\n".join([
            f"# {status}",
            "",
            "This is a diagnostic SEP/FUS decision, not a Mastrovito/TMVP claim.",
            "",
            "```json",
            json.dumps(evidence, indent=2, sort_keys=True),
            "```",
        ]),
        encoding="utf-8",
    )
    return decision_path
