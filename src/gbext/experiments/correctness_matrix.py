"""
Experiment: Correctness Matrix.

Validates functional equivalence between all 4 multiplication implementations
over the instances catalog.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from pathlib import Path
import random

from gbext.fields import irreducible
from gbext.types import Context
from gbext.baselines import direct_schoolbook, direct_karatsuba
from gbext.gbstyle import multiply_schoolbook, multiply_karatsuba

METHODS = {
    "direct_schoolbook": direct_schoolbook.multiply,
    "direct_karatsuba": direct_karatsuba.multiply,
    "gb_schoolbook": multiply_schoolbook.multiply,
    "gb_karatsuba_k": multiply_karatsuba.multiply
}

def generate_poly(degree_bound: int, p_full: int, m: int) -> list[int]:
    """Generate random canonical polynomial (degree < k) with random coefficients in GF(2^m)."""
    return [random.randint(0, (1 << m) - 1) for _ in range(degree_bound)]

def generate_modulus_g(k: int, p_full: int, m: int, family: str) -> list[int]:
    """Generate random ring modulus g(x) of degree k based on family."""
    g = [0] * (k + 1)
    g[k] = 1  # monic
    
    if family == "dense":
        for i in range(k):
            g[i] = random.randint(0, (1 << m) - 1)
    elif family == "trinomial":
        # x^k + a*x^j + b
        j = random.randint(1, k - 1)
        g[j] = random.randint(1, (1 << m) - 1)
        g[0] = random.randint(1, (1 << m) - 1)
    elif family == "pentanomial":
        indices = random.sample(range(1, k), 3)
        for idx in indices:
            g[idx] = random.randint(1, (1 << m) - 1)
        g[0] = random.randint(1, (1 << m) - 1)
    else: # fallback dense
        for i in range(k):
            g[i] = random.randint(0, (1 << m) - 1)
            
    return g

def run_correctness(instances_csv: str | Path, output_csv: str | Path, num_trials_per_instance: int = 5):
    """
    Run matrix of correctness tests.
    """
    df = pd.read_csv(instances_csv)
    results = []
    
    for _, row in df.iterrows():
        instance_id = row['instance_id']
        m = int(row['m'])
        k = int(row['k'])
        family = row['modulus_family']
        
        # Load field modulus (full form)
        p_full = irreducible.get_irreducible(m)
        
        for trial in range(num_trials_per_instance):
            g = generate_modulus_g(k, p_full, m, family)
            a = generate_poly(k, p_full, m)
            b = generate_poly(k, p_full, m)
            
            ctx = Context(track_timing=False, track_branches=False)
            
            baseline_result, _ = METHODS["direct_schoolbook"](a, b, g, p_full, m, ctx)
            
            for method_name, method_func in METHODS.items():
                if method_name == "direct_schoolbook":
                    passed = True
                else:
                    res, _ = method_func(a, b, g, p_full, m, ctx)
                    passed = (res == baseline_result)
                
                results.append({
                    "instance_id": instance_id,
                    "m": m,
                    "k": k,
                    "modulus_family": family,
                    "trial": trial,
                    "method": method_name,
                    "pass": passed
                })
                
    out_df = pd.DataFrame(results)
    
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    
    print(f"Correctness results saved to {out_path}")
    failed = out_df[out_df['pass'] == False]
    if not failed.empty:
        print("WARNING: Some tests failed!")
        print(failed)
    else:
        print("All correctness tests passed!")

if __name__ == "__main__":
    run_correctness("../../data/catalog/instances.csv", "../../results/correctness_summary.csv")
