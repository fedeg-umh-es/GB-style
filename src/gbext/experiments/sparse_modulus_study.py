"""
Experiment: Sparse Modulus Study.
Investigates performance impact of sparse vs dense moduli (families trinomial/pentanomial vs dense random).
"""

import pandas as pd
from pathlib import Path
from gbext.experiments.benchmark_matrix import run_benchmark

def run_sparse_study(config_path: Path, output_csv: Path):
    # This acts as a filtered shell targeting sparse vs dense instances
    print("Running sparse study...")
    pass
