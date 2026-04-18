"""
Experiment: Benchmark Matrix.

Measures operational performance of algorithms according to strict guidelines:
- Separate setup/inputs generation from timing
- Calculate mean, median, std_dev, ops/sec
- Record distinct accumulation vs reduction timings
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from pathlib import Path
import time
import json

from gbext.fields import irreducible
from gbext.types import Context
from gbext.experiments.correctness_matrix import METHODS, generate_poly, generate_modulus_g

def run_benchmark(instances_csv: str | Path, output_csv: str | Path, warmup_runs: int = 10, n_repetitions: int = 50):
    df = pd.read_csv(instances_csv)
    results = []
    
    for _, row in df.iterrows():
        instance_id = row['instance_id']
        m = int(row['m'])
        k = int(row['k'])
        family = row['modulus_family']
        
        p_full = irreducible.get_irreducible(m)
        g = generate_modulus_g(k, p_full, m, family)
        
        # Pre-generate common inputs to isolate generation out of timer
        inputs = [(generate_poly(k, p_full, m), generate_poly(k, p_full, m)) for _ in range(n_repetitions)]
        warmups = [(generate_poly(k, p_full, m), generate_poly(k, p_full, m)) for _ in range(warmup_runs)]
        
        ctx = Context(track_timing=True, track_branches=False)
        
        for method_name, method_func in METHODS.items():
            
            # 1. Warmup loop
            for (a, b) in warmups:
                method_func(a, b, g, p_full, m, ctx)
                
            # 2. Timing loop
            timings = []
            acc_timings = []
            red_timings = []
            
            for (a, b) in inputs:
                _, stats = method_func(a, b, g, p_full, m, ctx)
                timings.append(stats.total_time)
                acc_timings.append(stats.accumulation_time)
                red_timings.append(stats.reduction_time)
                
            # Compute stats
            mean_t = np.mean(timings)
            med_t = np.median(timings)
            std_t = np.std(timings)
            mean_acc = np.mean(acc_timings)
            mean_red = np.mean(red_timings)
            
            ops_per_sec = 1.0 / mean_t if mean_t > 0 else 0
            
            # To compute relative speedup properly later, we just dump absolute stats first
            results.append({
                "instance_id": instance_id,
                "m": m,
                "k": k,
                "modulus_family": family,
                "method": method_name,
                "mean_time": mean_t,
                "median_time": med_t,
                "std_time": std_t,
                "accumulation_time": mean_acc,
                "reduction_time": mean_red,
                "total_time": mean_t * n_repetitions, # Aggregate
                "ops_per_sec": ops_per_sec,
                "n_repetitions": n_repetitions,
                "warmup_runs": warmup_runs,
            })
            
    out_df = pd.DataFrame(results)
    
    # Calculate baseline relative speedups
    baselines = out_df[out_df['method'] == 'direct_schoolbook'].set_index('instance_id')
    out_df['relative_speedup'] = out_df.apply(
        lambda row: baselines.loc[row['instance_id'], 'mean_time'] / row['mean_time'] 
                    if row['instance_id'] in baselines.index and row['mean_time'] > 0 else 1.0, 
        axis=1
    )
    
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    print(f"Benchmark results saved to {out_path}")

if __name__ == "__main__":
    run_benchmark("../../data/catalog/instances.csv", "../../results/benchmark_summary.csv")
