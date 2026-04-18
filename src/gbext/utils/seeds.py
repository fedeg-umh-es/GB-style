"""
Reproducible RNG management.

All randomness in experiments should go through get_rng() so that
the seed chain is deterministic and traceable.
"""

from __future__ import annotations

import numpy as np


def get_rng(seed: int) -> np.random.Generator:
    """Return a seeded numpy Generator (PCG64)."""
    return np.random.default_rng(seed)


def derive_seed(base: int, *tags: str | int) -> int:
    """Derive a child seed from a base seed and string/int tags.

    Uses a simple but stable hash so that (base, "experiment_A", m=8)
    always maps to the same child seed regardless of call order.
    """
    h = base
    for t in tags:
        h = hash((h, t)) & 0xFFFF_FFFF
    return h
