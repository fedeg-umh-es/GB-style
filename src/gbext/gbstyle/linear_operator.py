"""
Explicit materialization of Linear Operators for GB-Style redundant convolution.

This module provides exact matrix construction for T(a) and R, which are mathematically
useful for testing equivalence on small (m, k).
For large sizes, the implicit algorithmic implementations in multiply_*.py are used.
"""

from __future__ import annotations
from gbext.fields import gf2m
import numpy as np

def build_toeplitz(a: list[int], k: int) -> list[list[int]]:
    """
    Build explicit (2k-1) x k Toeplitz matrix T(a) for polynomial a of degree < k.
    This maps coefficient vector of b (length k) to c (length 2k-1).
    """
    a_padded = a.copy()
    while len(a_padded) < k:
        a_padded.append(0)
        
    T = [[0]*k for _ in range(2*k - 1)]
    for row in range(2*k - 1):
        for col in range(k):
            idx = row - col
            if 0 <= idx < k:
                T[row][col] = a_padded[idx]
    return T

def matmul_gf2m(M: list[list[int]], v: list[int], p_full: int, m: int) -> list[int]:
    """
    Matrix-vector multiplication over GF(2^m).
    v is assumed a column vector of appropriate dimension.
    """
    rows = len(M)
    cols = len(M[0])
    if len(v) != cols:
        # pad v with zeros
        padded_v = v.copy()
        while len(padded_v) < cols:
            padded_v.append(0)
        v = padded_v
        
    res = [0]*rows
    for i in range(rows):
        acc = 0
        for j in range(cols):
            if v[j] and M[i][j]:
                acc ^= gf2m.mul(M[i][j], v[j], p_full, m)
        res[i] = acc
    return res

def build_reduction_matrix(g: list[int], k: int, p_full: int, m: int) -> list[list[int]]:
    """
    Build explicit k x (2k-1) reduction matrix R.
    Columns correspond exactly to x^0, x^1, ..., x^(2k-2) mod g.
    """
    # R is a matrix where the j-th column is the representation of x^j mod g
    from gbext.poly import core
    
    R = [[0]*(2*k - 1) for _ in range(k)]
    for j in range(2*k - 1):
        # build x^j
        xj = [0]*j + [1]
        rem = core.reduce_mod(xj, g, p_full, m)
        # place rem in column j
        for i in range(k):
            if i < len(rem):
                R[i][j] = rem[i]
    return R
