# gbext — GB-style Redundant Convolution over Extension Fields

Python library and experimental CLI for **GB-style redundant convolution arithmetic over GF(2^m)**.
Implements the Toeplitz-based decomposition of polynomial multiplication in quotient rings, alongside schoolbook and Karatsuba baselines, and a suite of reproducibility experiments.

## Overview

The GB-style formulation decomposes polynomial multiplication in `GF(2^m) = GF(2)[x] / g(x)` into:
1. A Toeplitz mapping via redundancy matrix `T(a)`
2. A fixed reduction step

This separation decouples accumulation from reduction, yielding more regular control flow and enabling structured cost analysis across `(m, k)` parameter pairs.

> **Warning:** "Regular control flow" and constant-time proxy metrics refer to algorithmic instruction layout only. They **do not** constitute a proof of side-channel resilience.

## Installation

```bash
pip install -e ".[dev]"          # editable install with dev dependencies
pip install -e ".[dev,numba]"    # include Numba-accelerated variants
```

Requires Python >= 3.11.

## Project Structure

```
src/gbext/
├── fields/          # GF(2^m) arithmetic and irreducible polynomial utilities
├── gbstyle/         # GB-style implementations (schoolbook, Karatsuba, linear operator)
├── baselines/       # Direct schoolbook and Karatsuba reference implementations
├── experiments/     # Reproducible experiment runners
├── cli/             # Typer-based CLI entry point
└── config.py        # Configuration loading
```

## CLI Usage

```bash
# Correctness verification
gbext run-correctness --config configs/default.yaml

# Benchmark all methods
gbext run-benchmark --config configs/default.yaml

# Sparse modulus cost study
gbext run-sparse-study --config configs/default.yaml

# Break-even analysis (theory vs empirical)
gbext run-break-even --config configs/default.yaml

# Constant-time proxy metrics
gbext run-ct-proxy --config configs/default.yaml

# Generate summary plots and reports
gbext make-report --input results/ --output results/summaries/
```

## Experiments

| Experiment | Output | Description |
|---|---|---|
| `correctness_matrix` | `correctness_summary.csv` | Verifies GB-style matches reference for all instances |
| `benchmark_matrix` | `benchmark_summary.csv` | Timing comparison across methods and `(m, k)` pairs |
| `sparse_modulus_study` | `sparse_ratios.csv` + plot | GB-style scaling for sparse `g(x)` |
| `break_even_study` | `theory_vs_empirical.csv` + plot | Theoretical vs measured break-even points |
| `ct_proxy_study` | `ct_proxy_stats.csv` + plot | Branch count / loop iteration proxy for CT analysis |

See [`docs/paper_mapping.md`](docs/paper_mapping.md) for the explicit mapping between theoretical claims, code modules, and experiments.

## Running Tests

```bash
pytest
pytest --cov=gbext        # with coverage
```

## License

MIT — Federico García Crespí \<fedeg@umh.es\>
