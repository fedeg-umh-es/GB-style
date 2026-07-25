# Codex runbook: FRONTIER_GATE

## Objective

Validate and execute the exact-operation SEP/FUS research gate. Do not measure
wall-clock time and do not draft a manuscript.

## Codex task

Use this repository and branch:

```text
repo: fedeg-umh-es/GB-style
branch: research/frontier-gate-q1
```

Execute the following sequence without changing the scientific model unless a
test demonstrates a defect.

### 1. Environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 2. Static inspection

Check:

- `src/gbext/frontier/dag.py`
- `src/gbext/frontier/architectures.py`
- `src/gbext/experiments/frontier_gate.py`
- `src/gbext/frontier/analysis.py`
- `tests/test_frontier_dag.py`
- `docs/RESEARCH_CONTRACT.md`

Verify that:

1. fan-out is free;
2. variable products are built once;
3. scalar multiples are shared only for the same signal and same constant;
4. no addition CSE occurs across outputs;
5. SEP and FUS use the same operation model;
6. no timing code enters FRONTIER_GATE.

### 3. Tests

```bash
pytest -q
```

On failure:

- stop the sweep;
- identify whether the defect is arithmetic, DAG evaluation, operation count,
  or model mismatch;
- fix the defect with the smallest change;
- add a regression test;
- rerun the full test suite.

Do not alter a counter merely to match an expected literature constant.

### 4. Small dry run

Create a temporary configuration derived from `configs/frontier_gate.yaml` with:

```yaml
m_values: [2]
k_values: [2, 3, 4]
max_supports_per_k_weight: 4
random_trials: 32
```

Run:

```bash
gbext run-frontier-gate --config /tmp/frontier_gate_small.yaml
```

Inspect:

```text
results/frontier_gate/frontier_gate.parquet
results/frontier_gate/frontier_gate_analyzed.parquet
results/frontier_gate/DECISION.md
```

Confirm that every row has:

- equal `mul_var` counts;
- finite operation counts;
- valid support and coefficient metadata;
- a deterministic discovery/holdout split;
- no timing columns.

### 5. Full run

```bash
gbext run-frontier-gate --config configs/frontier_gate.yaml
```

Do not modify thresholds after seeing the results.

### 6. Reproducibility check

Run the full command a second time and compare SHA-256 hashes of both Parquet
files and `DECISION.md`. They must be identical.

### 7. Deliverables

Commit only:

- code fixes and regression tests, if required;
- a short `results/frontier_gate/RUN_REPORT.md` containing environment versions,
  test result, row count, hashes and final decision;
- `DECISION.md`;
- a compact CSV summary if useful.

Do not commit the full Parquet files if repository policy excludes them. Preserve
them locally and report their hashes.

## Decision handling

### If `CLOSE_LINE`

Stop. Do not add another multiplier, tune the thresholds or draft a paper.

### If `PROMOTE_TO_TMVP`

Do not claim a Q1 gap yet. Open one issue titled:

```text
Implement source-matched TMVP_REF under FRONTIER_GATE model
```

The issue must name the exact primary paper, equations or algorithm, basis,
polynomial class, fan-in and sharing policy. No implementation starts until that
model-match document is complete.
