"""
Representation layer for GB-style polynomials.

Provides mappings between Canonical State (elements in GF(2^m)[x]/<g(x)> of degree < k)
and Redundant State (elements in GF(2^m)[x] of degree < 2k-1).
"""

from __future__ import annotations
from gbext.poly import core

def canonical_to_redundant(a: list[int], k: int) -> list[int]:
    """
    Pad canonical form (degree < k) to redundant vector space dimension (2k-1).
    Operationally, this is just an injection.
    """
    res = a.copy()
    while len(res) < 2 * k - 1:
        res.append(0)
    return res

def redundant_to_canonical(a_red: list[int], g: list[int], k: int, p_full: int, m: int) -> list[int]:
    """
    Map from redundant form (2k-1 dimension) to canonical form (k dimension).
    This applies the fixed linear reduction R.
    For efficiency in the baseline implementation, we use procedural reduction,
    but logically this defines the surjective R fixed map.
    """
    # ensure it strictly fits in redundant space
    max_len = 2 * k - 1
    if len(a_red) > max_len:
        a_red = a_red[:max_len]
        
    c_can = core.reduce_mod(a_red, g, p_full, m)
    while len(c_can) < k:
        c_can.append(0)
    return c_can
