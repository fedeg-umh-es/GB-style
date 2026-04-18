"""
Baseline implementation of Direct Karatsuba Multiplication over GF(2^m)[x]/<g(x)>.
"""

from __future__ import annotations
import time
from gbext.poly import core
from gbext.types import Context, Stats

def multiply(a: list[int], b: list[int], g: list[int], p_full: int, m: int, ctx: Context) -> tuple[list[int], Stats]:
    """
    Directly multiply a and b in GF(2^m)[x] using Karatsuba, then reduce modulo g.
    """
    stats = Stats()
    
    start_time = time.perf_counter() if ctx.track_timing else 0
    
    # 1. Karatsuba multiplication
    start_mul = time.perf_counter() if ctx.track_timing else 0
    c_unreduced = core.mul_karatsuba(a, b, p_full, m)
    if ctx.track_timing:
        stats.accumulation_time = time.perf_counter() - start_mul
        
    # 2. Modulo reduction
    start_red = time.perf_counter() if ctx.track_timing else 0
    c_reduced = core.reduce_mod(c_unreduced, g, p_full, m)
    if ctx.track_timing:
        stats.reduction_time = time.perf_counter() - start_red
        stats.total_time = time.perf_counter() - start_time
        
    if ctx.track_branches:
        # Proxy complexity O(n^1.58)
        n = max(len(a), len(b))
        stats.iteration_count = int(n ** 1.585)
        
    return c_reduced, stats
