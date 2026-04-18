"""
GB-style Schoolbook Multiplication.
Explicit separation of Redundant Accumulation (Toeplitz mapping) and Fixed Reduction (R map).
"""

from __future__ import annotations
import time
from gbext.poly import core
from gbext.types import Context, Stats
from gbext.gbstyle import representation

def multiply(a: list[int], b: list[int], g: list[int], p_full: int, m: int, ctx: Context) -> tuple[list[int], Stats]:
    """
    GB-style Schoolbook multiply.
    """
    stats = Stats()
    
    k = len(g) - 1 # assuming g is degree k
    
    start_time = time.perf_counter() if ctx.track_timing else 0
    
    # 1. Accumulation into redundant State
    # Mathematically: c_red = T(a) * b
    start_mul = time.perf_counter() if ctx.track_timing else 0
    
    # We implicitly evaluate T_a * b via polynomial multiplication exactly as degree k-1 logic
    a_norm = a.copy()
    b_norm = b.copy()
    while len(a_norm) < k: a_norm.append(0)
    while len(b_norm) < k: b_norm.append(0)
    
    c_red_unpadded = core.mul_schoolbook(a_norm, b_norm, p_full, m)
    c_red = representation.canonical_to_redundant(c_red_unpadded, k)
    
    if ctx.track_timing:
        stats.accumulation_time = time.perf_counter() - start_mul
        
    # 2. Fixed Modulo Reduction
    # Mathematically: c_can = R * c_red
    start_red = time.perf_counter() if ctx.track_timing else 0
    
    c_can = representation.redundant_to_canonical(c_red, g, k, p_full, m)
    
    if ctx.track_timing:
        stats.reduction_time = time.perf_counter() - start_red
        stats.total_time = time.perf_counter() - start_time
        
    if ctx.track_branches:
        stats.iteration_count = k * k
        
    return c_can, stats
