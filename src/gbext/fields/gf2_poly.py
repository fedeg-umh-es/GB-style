"""
Binary polynomial arithmetic (GF(2)[x]).

Elements are non-negative Python integers, bit i represents the coefficient of x^i.
All operations are exact; no modular reduction unless explicitly requested.

This module is the foundation for GF(2^m) construction.
"""

from __future__ import annotations


def degree(a: int) -> int:
    """Degree of a non-zero binary polynomial; -1 for the zero polynomial."""
    return a.bit_length() - 1


def add(a: int, b: int) -> int:
    """Addition (= XOR) in GF(2)[x]."""
    return a ^ b


def mul(a: int, b: int) -> int:
    """
    Multiplication in GF(2)[x] via schoolbook carry-less multiplication.

    Cost: O(deg(a) * deg(b)) XOR operations.
    For correctness testing; not performance-critical.
    """
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        b >>= 1
    return result


def divmod_gf2(a: int, b: int) -> tuple[int, int]:
    """
    Euclidean division in GF(2)[x]: returns (quotient, remainder).

    a = q * b + r  with deg(r) < deg(b).
    Raises ZeroDivisionError if b == 0.
    """
    if b == 0:
        raise ZeroDivisionError("division by zero polynomial")
    q = 0
    r = a
    db = degree(b)
    while True:
        dr = degree(r)
        if dr < db:
            break
        shift = dr - db
        q ^= (1 << shift)
        r ^= (b << shift)
    return q, r


def mod(a: int, m: int) -> int:
    """Reduce a modulo m in GF(2)[x]."""
    _, r = divmod_gf2(a, m)
    return r


def gcd(a: int, b: int) -> int:
    """GCD in GF(2)[x] via Euclidean algorithm."""
    while b:
        _, r = divmod_gf2(a, b)
        a, b = b, r
    return a


def is_irreducible(f: int) -> bool:
    """
    Test irreducibility of f in GF(2)[x] via Ben-Or's algorithm.

    A polynomial f of degree n is irreducible iff:
      1. gcd(f, x^(2^i) - x) == 1  for i = 1, ..., floor(n/2)
      2. (equivalently) f has no factor of degree <= n/2

    Uses the fact that x^(2^i) mod f can be computed by repeated squaring.
    """
    n = degree(f)
    if n <= 0:
        return False
    if n == 1:
        return True

    # x^(2^i) mod f via repeated squaring
    x_pow = 2  # represents x^1
    for _ in range(1, n // 2 + 1):
        # square: x_pow -> x_pow^2 mod f
        x_pow = mod(mul(x_pow, x_pow), f)
        # gcd(x_pow XOR x, f) must be 1
        g = gcd(x_pow ^ 2, f)  # x^(2^i) - x = x^(2^i) XOR x
        if g != 1:
            return False
    return True


def poly_to_str(a: int) -> str:
    """Human-readable representation, e.g. 'x^4 + x + 1'."""
    if a == 0:
        return "0"
    terms = []
    for i in range(degree(a), -1, -1):
        if (a >> i) & 1:
            if i == 0:
                terms.append("1")
            elif i == 1:
                terms.append("x")
            else:
                terms.append(f"x^{i}")
    return " + ".join(terms)
