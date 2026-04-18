"""
Configuration loading and validation for gbext experiments.

All experiment parameters flow through ExperimentConfig, loaded from YAML.
Downstream modules receive config objects, never raw dicts.
"""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class FieldConfig:
    m_values: list[int] = field(default_factory=lambda: [4, 8])
    irreducibles: dict[int, int] = field(default_factory=dict)
    backend: str = "poly"  # "poly" | "table"


@dataclass
class PolyConfig:
    k_values: list[int] = field(default_factory=lambda: [4, 8])
    dense_moduli: bool = True
    sparse_moduli: bool = True


@dataclass
class BenchmarkConfig:
    n_trials: int = 100
    warmup: int = 10
    batch_sizes: list[int] = field(default_factory=lambda: [1])
    methods: list[str] = field(default_factory=lambda: [
        "direct_schoolbook", "direct_karatsuba",
        "gb_schoolbook", "gb_karatsuba_k",
    ])


@dataclass
class CorrectnessConfig:
    m_values: list[int] = field(default_factory=lambda: [2, 4, 8])
    k_values: list[int] = field(default_factory=lambda: [2, 4, 8])
    n_pairs_per_config: int = 50


@dataclass
class SparseStudyConfig:
    sparsity_levels: list[int] = field(default_factory=lambda: [1, 2, 3, 5])
    n_random_moduli_per_sparsity: int = 5
    n_trials: int = 200
    warmup: int = 20


@dataclass
class CtProxyConfig:
    n_random_inputs: int = 1000
    methods: list[str] = field(default_factory=lambda: ["direct_schoolbook", "gb_schoolbook"])
    collect_timing_variance: bool = True
    collect_branch_counts: bool = True
    collect_access_counts: bool = True


@dataclass
class ExperimentConfig:
    seed: int = 42
    output_dir: Path = Path("results")
    log_level: str = "INFO"

    fields: FieldConfig = field(default_factory=FieldConfig)
    poly: PolyConfig = field(default_factory=PolyConfig)
    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig)
    correctness: CorrectnessConfig = field(default_factory=CorrectnessConfig)
    sparse_study: SparseStudyConfig = field(default_factory=SparseStudyConfig)
    ct_proxy: CtProxyConfig = field(default_factory=CtProxyConfig)


def _coerce(cls, data: dict):
    """Recursively coerce a dict into a dataclass instance."""
    if not isinstance(data, dict):
        return data
    hints = cls.__dataclass_fields__
    kwargs = {}
    for name, f in hints.items():
        if name not in data:
            kwargs[name] = f.default if f.default is not f.default_factory else f.default_factory()  # type: ignore[misc]
            continue
        val = data[name]
        # Recurse into nested dataclasses
        tp = f.type
        if isinstance(tp, str):
            tp = eval(tp)  # noqa: S307
        if hasattr(tp, "__dataclass_fields__"):
            val = _coerce(tp, val)
        kwargs[name] = val
    return cls(**kwargs)


def load_config(path: str | Path) -> ExperimentConfig:
    """Load an ExperimentConfig from a YAML file."""
    with open(path) as fh:
        raw = yaml.safe_load(fh)

    exp_raw = raw.get("experiment", {})
    cfg = ExperimentConfig(
        seed=exp_raw.get("seed", 42),
        output_dir=Path(exp_raw.get("output_dir", "results")),
        log_level=exp_raw.get("log_level", "INFO"),
    )

    if "fields" in raw:
        d = raw["fields"]
        cfg.fields = FieldConfig(
            m_values=d.get("m_values", cfg.fields.m_values),
            irreducibles={int(k): v for k, v in d.get("irreducibles", {}).items()},
            backend=d.get("backend", "poly"),
        )
    if "poly" in raw:
        d = raw["poly"]
        cfg.poly = PolyConfig(
            k_values=d.get("k_values", cfg.poly.k_values),
            dense_moduli=d.get("dense_moduli", True),
            sparse_moduli=d.get("sparse_moduli", True),
        )
    if "benchmark" in raw:
        d = raw["benchmark"]
        cfg.benchmark = BenchmarkConfig(**{k: v for k, v in d.items()})
    if "correctness" in raw:
        d = raw["correctness"]
        cfg.correctness = CorrectnessConfig(**{k: v for k, v in d.items()})
    if "sparse_study" in raw:
        d = raw["sparse_study"]
        cfg.sparse_study = SparseStudyConfig(**{k: v for k, v in d.items()})
    if "ct_proxy" in raw:
        d = raw["ct_proxy"]
        cfg.ct_proxy = CtProxyConfig(**{k: v for k, v in d.items()})

    return cfg
