"""
Wall-clock timing utilities for microbenchmarks.

Uses time.perf_counter_ns for sub-microsecond resolution.
All public functions return times in seconds (float) for consistency.
"""

from __future__ import annotations

import time
import statistics
from collections.abc import Callable
from typing import Any


def timeit_ns(fn: Callable, *args, n: int = 100, warmup: int = 10, **kwargs) -> dict[str, float]:
    """
    Time a callable over n repetitions after warmup.

    Returns a dict with keys: mean_s, std_s, min_s, max_s, median_s, ops_per_s.
    All times in seconds.
    """
    for _ in range(warmup):
        fn(*args, **kwargs)

    times_ns: list[int] = []
    for _ in range(n):
        t0 = time.perf_counter_ns()
        fn(*args, **kwargs)
        times_ns.append(time.perf_counter_ns() - t0)

    times_s = [t * 1e-9 for t in times_ns]
    mean_s = statistics.mean(times_s)
    return {
        "mean_s": mean_s,
        "std_s": statistics.stdev(times_s) if len(times_s) > 1 else 0.0,
        "min_s": min(times_s),
        "max_s": max(times_s),
        "median_s": statistics.median(times_s),
        "ops_per_s": 1.0 / mean_s if mean_s > 0 else float("inf"),
        "n_trials": n,
    }


def speedup(baseline: dict[str, float], candidate: dict[str, float]) -> float:
    """Return baseline.mean / candidate.mean (>1 means candidate is faster)."""
    return baseline["mean_s"] / candidate["mean_s"]
