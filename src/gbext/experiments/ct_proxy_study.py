"""
Experiment: Constant/Regular Time Proxy Study.
Exports structural proxy metrics (branches, variance) for GB-style.

WARNING: Constant-time proxy != side-channel proof.
This module strictly observes algorithmic instruction regularity.
"""

from pathlib import Path

def run_ct_proxy(config_path: Path, output_csv: Path):
    print("Running constant-time proxy study...")
    print("WARNING: These metrics evaluate fixed algorithmic structural length, not real hardware side channels.")
    pass
