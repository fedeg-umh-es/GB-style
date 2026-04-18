"""
GB-style Karatsuba Multiplication.

Documenting precision on Karatsuba usage:
In the GB-style paradigm, we decompose the multiplication over the quotient ring into
two independent phases:
1. Redundant Accumulation (the polynomial multiplication phase over GF(2^m)[x])
2. Fixed Reduction (the map from the 2k-1 spatial representation back to k)

Karatsuba is strictly applied ONLY to the Phase 1 (Redundant Accumulation).
The fixed mathematical reduction R applied in Phase 2 ignores the sub-quadratic 
structure, enforcing a regular fixed layout regardless of data shape.
"""

from __future__ import annotations
import time
from gbext.poly import core
from gbext.types import Context, Stats
from gbext.gbstyle import representation

def multiply(a: list[int], b: list[int], g: list[int], p_full: int, m: int, ctx: Context) -> tuple[list[int], Stats]:
    """
    GB-style Karatsuba multiply.
    """
    stats = Stats()
    k = len(g) - 1
    
    start_time = time.perf_counter() if ctx.track_timing else 0
    
    # 1. Accumulation into redundant State
    # Karatsuba strictly applies HERE to generate the 2k-1 array.
    start_mul = time.perf_counter() if ctx.track_timing else 0
    
    a_norm = a.copy()
    b_norm = b.copy()
    while len(a_norm) < k: a_norm.append(0)
    while len(b_norm) < k: b_norm.append(0)
    
    c_red_unpadded = core.mul_karatsuba(a_norm, b_norm, p_full, m)
    c_red = representation.canonical_to_redundant(c_red_unpadded, k)
    
    if ctx.track_timing:
        stats.accumulation_time = time.perf_counter() - start_mul
        
    # 2. Fixed Modulo Reduction
    # Reduction is purely procedural/matrix-based and oblivious to Karatsuba.
    start_red = time.perf_counter() if ctx.track_timing else 0
    
    c_can = representation.redundant_to_canonical(c_red, g, k, p_full, m)
    
    if ctx.track_timing:
        stats.reduction_time = time.perf_counter() - start_red
        stats.total_time = time.perf_counter() - start_time
        
    if ctx.track_branches:
        stats.iteration_count = int(k ** 1.585)
        
    return c_can, stats
