"""
Polynomial arithmetic over GF(2^m).

Polynomials are represented as lists of integers (GF(2^m) elements), 
where index i is the coefficient of x^i.
"""

from __future__ import annotations
from gbext.fields import gf2m

Polynomial = list[int]

def normalize(a: Polynomial) -> Polynomial:
    """Remove leading zeros."""
    while a and a[-1] == 0:
        a.pop()
    return a

def degree(a: Polynomial) -> int:
    """Degree of a polynomial (-1 if zero)."""
    return len(normalize(a)) - 1

def add(a: Polynomial, b: Polynomial) -> Polynomial:
    """Polynomial addition (XOR of coefficients)."""
    n, m = len(a), len(b)
    res = []
    for i in range(max(n, m)):
        c_a = a[i] if i < n else 0
        c_b = b[i] if i < m else 0
        res.append(c_a ^ c_b)
    return normalize(res)

def mul_scalar(a: Polynomial, scalar: int, p_full: int, m: int) -> Polynomial:
    """Multiply polynomial by a scalar in GF(2^m)."""
    if scalar == 0:
        return []
    return [gf2m.mul(c, scalar, p_full, m) for c in a]

def mul_schoolbook(a: Polynomial, b: Polynomial, p_full: int, m: int) -> Polynomial:
    """Schoolbook multiplication in GF(2^m)[x]."""
    if not a or not b:
        return []
    na, nb = len(a), len(b)
    res = [0] * (na + nb - 1)
    for i, c_a in enumerate(a):
        if c_a == 0:
            continue
        for j, c_b in enumerate(b):
            res[i + j] ^= gf2m.mul(c_a, c_b, p_full, m)
    return normalize(res)

def mul_karatsuba(a: Polynomial, b: Polynomial, p_full: int, m: int, cutoff: int = 4) -> Polynomial:
    """Karatsuba multiplication in GF(2^m)[x]."""
    a = normalize(a.copy())
    b = normalize(b.copy())
    
    if not a or not b:
        return []
    
    n = max(len(a), len(b))
    if n <= cutoff:
        return mul_schoolbook(a, b, p_full, m)
        
    k = (n + 1) // 2
    
    a0, a1 = a[:k], a[k:]
    b0, b1 = b[:k], b[k:]
    
    z0 = mul_karatsuba(a0, b0, p_full, m, cutoff)
    z2 = mul_karatsuba(a1, b1, p_full, m, cutoff)
    
    a_sum = add(a0, a1)
    b_sum = add(b0, b1)
    
    z1_temp = mul_karatsuba(a_sum, b_sum, p_full, m, cutoff)
    z1 = add(add(z1_temp, z0), z2)
    
    # Assembly: z0 + z1*x^k + z2*x^(2k)
    res = z0.copy()
    
    # Add z1 shifted by k
    while len(res) < len(z1) + k:
        res.append(0)
    for i, coeff in enumerate(z1):
        res[i + k] ^= coeff
        
    # Add z2 shifted by 2k
    while len(res) < len(z2) + 2*k:
        res.append(0)
    for i, coeff in enumerate(z2):
        res[i + 2*k] ^= coeff
        
    return normalize(res)

def reduce_mod(a: Polynomial, g: Polynomial, p_full: int, m: int) -> Polynomial:
    """
    Procedural modulo reduction in GF(2^m)[x].
    Returns a mod g. 
    g is assumed monic for simplicity, or we will just use leading coeff division.
    """
    g = normalize(g.copy())
    if not g:
        raise ZeroDivisionError("Modulo by zero polynomial")
        
    dg = degree(g)
    a = normalize(a.copy())
    
    lc_g_inv = gf2m.inv(g[-1], p_full, m) if g[-1] != 1 else 1
    
    while degree(a) >= dg:
        da = degree(a)
        shift = da - dg
        # factor to eliminate leading term
        factor = gf2m.mul(a[-1], lc_g_inv, p_full, m)
        
        # subtract (XOR) factor * g * x^shift from a
        for i, cg in enumerate(g):
            if cg:
                val = gf2m.mul(cg, factor, p_full, m)
                a[i + shift] ^= val
                
        # ensure pop correctly
        a.pop()
        a = normalize(a)
        
    return a
