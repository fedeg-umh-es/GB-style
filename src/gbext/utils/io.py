"""
Result persistence: CSV, Parquet, JSON metadata.
"""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd


def save_csv(df: pd.DataFrame, path: str | Path, *, index: bool = False) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=index)
    return p


def save_parquet(df: pd.DataFrame, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(p, index=False)
    return p


def save_metadata(meta: dict, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as fh:
        json.dump(meta, fh, indent=2, default=str)
    return p


def load_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)
