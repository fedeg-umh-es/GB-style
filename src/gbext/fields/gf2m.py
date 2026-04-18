"""
GF(2^m) arithmetic — polynomial backend.

An element of GF(2^m) is represented as an integer in [0, 2^m),
where bit i is the coefficient of alpha^i (alpha = root of the
irreducible polynomial p(x)).

Operations:
  add(a, b)       -- XOR
  mul(a, b, p, m) -- carry-less multiply then reduce mod p
  inv(a, p, m)    -- extended Euclidean
  pow_elem(a, e)  -- repeated squaring
  div(a, b)       -- a * inv(b)

The irreducible p is stored as its FULL bitmask (degree-m bit included).
"""

from __future__ import annotations

from gbext.fields import gf2_poly as _p


def add(a: int, b: int) -> int:
    """Addition in GF(2^m): bitwise XOR."""
    return a ^ b


def _reduce(product: int, p_full: int, m: int) -> int:
    """
    Reduce a binary polynomial 'product' of degree < 2m modulo p_full.

    p_full has degree m (the leading bit at position m is 1).
    We XOR p_full shifted appropriately for each bit of product above degree m-1.
    """
    mask = (1 << m) - 1
    # Process bits from degree 2m-2 down to m
    for i in range(2 * m - 2, m - 1, -1):
        if (product >> i) & 1:
            product ^= p_full << (i - m)
    return product & mask


def mul(a: int, b: int, p_full: int, m: int) -> int:
    """
    Multiplication in GF(2^m): carry-less mul then reduce.

    Uses schoolbook CLMUL; correct for any m.
    """
    # Carry-less multiplication
    product = _p.mul(a, b)
    return _reduce(product, p_full, m)


def mul_fast(a: int, b: int, p_full: int, m: int) -> int:
    """
    Shift-and-add multiplication that reduces on the fly (left-to-right).

    Avoids building the full 2m-bit product.  Same result as mul().
    """
    result = 0
    high_bit = 1 << (m - 1)
    mask = (1 << m) - 1
    p_lower = p_full ^ (1 << m)  # lower-m bits of p

    for _ in range(m):
        if b & 1:
            result ^= a
        b >>= 1
        carry = a & high_bit
        a = (a << 1) & mask
        if carry:
            a ^= p_lower
    return result


def sq(a: int, p_full: int, m: int) -> int:
    """Square in GF(2^m). Uses mul_fast for now; a sparse-polynomial fast path is TODO."""
    return mul_fast(a, a, p_full, m)


def pow_elem(a: int, e: int, p_full: int, m: int) -> int:
    """Exponentiation by repeated squaring."""
    if e == 0:
        return 1
    result = 1
    base = a
    while e:
        if e & 1:
            result = mul_fast(result, base, p_full, m)
        base = sq(base, p_full, m)
        e >>= 1
    return result


def inv(a: int, p_full: int, m: int) -> int:
    """
    Inverse via Fermat's little theorem: a^{2^m - 2}.

    Alternatively one could use extended Euclidean; Fermat is simpler
    to implement correctly and the cost difference is negligible for
    the parameter ranges we study.
    """
    if a == 0:
        raise ZeroDivisionError("inverse of zero")
    return pow_elem(a, (1 << m) - 2, p_full, m)


def div(a: int, b: int, p_full: int, m: int) -> int:
    """Division: a / b = a * inv(b)."""
    return mul_fast(a, inv(b, p_full, m), p_full, m)


def random_element(rng, m: int) -> int:
    """Uniform random non-zero element of GF(2^m)."""
    return int(rng.integers(1, 1 << m))


def random_elements(rng, m: int, n: int) -> list[int]:
    """n uniform random elements (may include 0)."""
    return [int(x) for x in rng.integers(0, 1 << m, size=n)]
