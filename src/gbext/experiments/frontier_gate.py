"""Binary research gate for separated versus diagnostic fused multiplication.

This experiment counts exact operations in GF(2^m). It performs no timing.
A positive result only promotes the project to a model-matched TMVP/Mastrovito
comparison; it is not, by itself, a publication claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import asdict
from itertools import combinations
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from gbext.fields import irreducible
from gbext.frontier.architectures import (
    build_fus_dag,
    build_sep_dag,
    constant_break_even,
    weighted_delta,
)
from gbext.gbstyle.linear_operator import build_reduction_matrix
from gbext.poly import core

MODEL_VERSION = "frontier-gate-v1"


def _stable_int(*parts: object) -> int:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def _support_candidates(k: int, weight: int, limit: int, seed: int) -> list[tuple[int, ...]]:
    """Return deterministic support tuples including exponent zero."""
    if weight < 2 or weight > k + 1:
        raise ValueError("weight must include leading and constant terms")
    internal_count = weight - 2
    if internal_count == 0:
        return [(0,)]

    all_internal = list(combinations(range(1, k), internal_count))
    ranked = sorted(all_internal, key=lambda item: _stable_int(seed, k, weight, item))
    selected = ranked[:limit]

    # Inject geometrically interpretable cases when available.
    anchors: list[tuple[int, ...]] = []
    if internal_count == 1:
        for value in {1, max(1, k // 2), k - 1}:
            anchors.append((value,))
    elif internal_count == 3 and k >= 5:
        anchors.extend([
            (1, 2, 3),
            tuple(sorted({1, max(2, k // 2), k - 1})),
            (k - 3, k - 2, k - 1),
        ])

    merged: list[tuple[int, ...]] = []
    for item in anchors + selected:
        if len(item) == internal_count and item not in merged:
            merged.append(item)
    return [(0, *item) for item in merged[:limit]]


def _coefficient_sets(support: tuple[int, ...], m: int, classes: list[str]) -> list[tuple[str, dict[int, int]]]:
    nonzero_mask = (1 << m) - 1
    results: list[tuple[str, dict[int, int]]] = []
    for coefficient_class in classes:
        if coefficient_class == "binary":
            mapping = {exponent: 1 for exponent in support}
        elif coefficient_class == "repeated_nonunit":
            gamma = 2 & nonzero_mask
            if gamma in {0, 1}:
                gamma = 3 & nonzero_mask
            mapping = {exponent: gamma for exponent in support}
        elif coefficient_class == "distinct_nonunit":
            values = [value for value in range(2, 1 << m)]
            if len(values) < len(support):
                continue
            mapping = {exponent: values[index] for index, exponent in enumerate(support)}
        else:
            raise ValueError(f"Unknown coefficient class: {coefficient_class}")
        results.append((coefficient_class, mapping))
    return results


def _make_modulus(k: int, coefficients: dict[int, int]) -> list[int]:
    g = [0] * (k + 1)
    for exponent, coefficient in coefficients.items():
        g[exponent] = coefficient
    g[k] = 1
    return g


def _pad(values: list[int], length: int) -> list[int]:
    return values[:length] + [0] * max(0, length - len(values))


def _validate_dags(
    g: list[int],
    p_full: int,
    m: int,
    sep_dag: Any,
    sep_outputs: list[int],
    fus_dag: Any,
    fus_outputs: list[int],
    trials: int,
    seed: int,
) -> None:
    k = len(g) - 1
    rng = random.Random(seed)
    cases: list[tuple[list[int], list[int]]] = []
    if (1 << (m * k)) <= 256:
        vectors = [
            [(encoded >> (m * index)) & ((1 << m) - 1) for index in range(k)]
            for encoded in range(1 << (m * k))
        ]
        cases = [(a, b) for a in vectors for b in vectors]
    else:
        cases = [
            (
                [rng.randrange(1 << m) for _ in range(k)],
                [rng.randrange(1 << m) for _ in range(k)],
            )
            for _ in range(trials)
        ]

    for a, b in cases:
        reference = _pad(core.reduce_mod(core.mul_schoolbook(a, b, p_full, m), g, p_full, m), k)
        inputs = {**{f"a{i}": value for i, value in enumerate(a)}, **{f"b{i}": value for i, value in enumerate(b)}}
        sep_value = sep_dag.evaluate(sep_outputs, inputs, p_full, m)
        fus_value = fus_dag.evaluate(fus_outputs, inputs, p_full, m)
        if sep_value != reference or fus_value != reference:
            raise AssertionError(
                f"Functional gate failed for m={m}, k={k}, g={g}, a={a}, b={b}: "
                f"reference={reference}, sep={sep_value}, fus={fus_value}"
            )


def _matrix_features(g: list[int], p_full: int, m: int) -> dict[str, float | int]:
    k = len(g) - 1
    reduction = build_reduction_matrix(g, k, p_full, m)
    nonzero = sum(value != 0 for row in reduction for value in row)
    total = k * (2 * k - 1)
    column_weights = [sum(reduction[row][column] != 0 for row in range(k)) for column in range(2 * k - 1)]
    return {
        "reduction_density": nonzero / total,
        "reduction_nonzeros": nonzero,
        "column_weight_min": min(column_weights),
        "column_weight_max": max(column_weights),
        "column_weight_mean": sum(column_weights) / len(column_weights),
    }


def _decision(rows: list[dict[str, Any]], config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    gate = config["decision"]
    rho_grid = [float(value) for value in config["cost_model"]["rho_const_grid"]]

    candidate_rows = []
    for row in rows:
        signs = set()
        for rho_const in rho_grid:
            delta = row["delta_add"] + rho_const * row["delta_mul_const"]
            signs.add(0 if math.isclose(delta, 0.0, abs_tol=1e-12) else (1 if delta > 0 else -1))
        if -1 in signs and 1 in signs:
            candidate_rows.append(row)

    degrees = {row["k"] for row in candidate_rows}
    supports = {row["support"] for row in candidate_rows}
    promote = (
        len(candidate_rows) >= int(gate["min_candidate_instances"])
        and len(degrees) >= int(gate["min_distinct_k"])
        and len(supports) >= int(gate["min_distinct_supports"])
    )
    status = "PROMOTE_TO_TMVP" if promote else "CLOSE_LINE"
    evidence = {
        "candidate_instances": len(candidate_rows),
        "distinct_k": sorted(degrees),
        "distinct_supports": len(supports),
        "rho_const_grid": rho_grid,
        "interpretation": (
            "Diagnostic SEP/FUS frontier found; implement and compare TMVP_REF before any publication claim."
            if promote
            else "No stable diagnostic frontier under the preregistered gate; close the line."
        ),
    }
    return status, evidence


def run_frontier_gate(config_path: str | Path) -> tuple[Path, Path]:
    config_path = Path(config_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    output_dir = Path(config["experiment"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    seed = int(config["experiment"]["seed"])
    validation_trials = int(config["validation"]["random_trials"])
    rows: list[dict[str, Any]] = []

    for m in config["grid"]["m_values"]:
        m = int(m)
        p_full = irreducible.get_irreducible(m)
        for k in config["grid"]["k_values"]:
            k = int(k)
            for weight in config["grid"]["weights"]:
                weight = int(weight)
                if weight > k + 1:
                    continue
                supports = _support_candidates(
                    k=k,
                    weight=weight,
                    limit=int(config["grid"]["max_supports_per_k_weight"]),
                    seed=seed,
                )
                for support in supports:
                    for coefficient_class, coefficient_map in _coefficient_sets(
                        support, m, list(config["grid"]["coefficient_classes"])
                    ):
                        g = _make_modulus(k, coefficient_map)
                        sep_dag, sep_outputs, sep = build_sep_dag(g, p_full, m)
                        fus_dag, fus_outputs, fus = build_fus_dag(g, p_full, m)

                        _validate_dags(
                            g,
                            p_full,
                            m,
                            sep_dag,
                            sep_outputs,
                            fus_dag,
                            fus_outputs,
                            trials=validation_trials,
                            seed=_stable_int(seed, m, k, support, coefficient_class),
                        )

                        matrix_features = _matrix_features(g, p_full, m)
                        rho_star = constant_break_even(sep, fus)
                        row = {
                            "model_version": MODEL_VERSION,
                            "m": m,
                            "k": k,
                            "support": json.dumps(support),
                            "coefficients": json.dumps(coefficient_map, sort_keys=True),
                            "coefficient_class": coefficient_class,
                            "weight": weight,
                            "max_exponent_ratio": max(support) / k,
                            "num_exponents_above_half": sum(exponent > k / 2 for exponent in support),
                            "mul_var_sep": sep.mul_var,
                            "mul_const_sep": sep.mul_const,
                            "add_sep": sep.add,
                            "depth_sep": sep.depth,
                            "nodes_sep": sep.nodes,
                            "mul_var_fus": fus.mul_var,
                            "mul_const_fus": fus.mul_const,
                            "add_fus": fus.add,
                            "depth_fus": fus.depth,
                            "nodes_fus": fus.nodes,
                            "delta_mul_var": sep.mul_var - fus.mul_var,
                            "delta_mul_const": sep.mul_const - fus.mul_const,
                            "delta_add": sep.add - fus.add,
                            "delta_depth": sep.depth - fus.depth,
                            "rho_const_star": rho_star,
                            **matrix_features,
                        }
                        for rho_const in config["cost_model"]["rho_const_grid"]:
                            row[f"delta_cost_rho_{rho_const}"] = weighted_delta(
                                sep,
                                fus,
                                rho_var=float(config["cost_model"]["rho_var"]),
                                rho_const=float(rho_const),
                            )
                        rows.append(row)

    status, evidence = _decision(rows, config)
    parquet_path = output_dir / "frontier_gate.parquet"
    decision_path = output_dir / "DECISION.md"
    pd.DataFrame(rows).to_parquet(parquet_path, index=False)

    decision_path.write_text(
        "\n".join([
            f"# {status}",
            "",
            "## Scope",
            "This decision concerns SEP_SB versus the diagnostic FUS_CAN only.",
            "It is not evidence of superiority over Mastrovito or TMVP.",
            "",
            "## Evidence",
            "```json",
            json.dumps(evidence, indent=2, sort_keys=True),
            "```",
            "",
            "## Mandatory next action",
            (
                "Implement a named, source-matched TMVP_REF architecture and repeat the gate."
                if status == "PROMOTE_TO_TMVP"
                else "Stop. Do not open a manuscript or another multiplier variant."
            ),
        ]),
        encoding="utf-8",
    )
    return parquet_path, decision_path
