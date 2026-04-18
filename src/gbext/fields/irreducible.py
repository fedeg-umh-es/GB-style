"""
Catalogue of irreducible polynomials over GF(2) and utilities for finding them.

Polynomials are represented as integers (bit i = coefficient of x^i).
The degree-m coefficient is always 1, so a degree-m poly fits in m+1 bits.

Standard catalog sources:
  - Lidl & Niederreiter, "Finite Fields"
  - NIST FIPS 186 / IEEE 1363 appendices
"""

from __future__ import annotations

from gbext.fields.gf2_poly import is_irreducible, degree


# Hard-coded table of well-known irreducible polys indexed by degree.
# Each entry is the full bitmask including the leading 1.
# Multiple entries per degree when useful (dense, trinomial, pentanomial).
KNOWN_IRREDUCIBLES: dict[int, list[int]] = {
    2:  [0b111],                    # x^2+x+1
    3:  [0b1011, 0b1101],           # x^3+x+1, x^3+x^2+1
    4:  [0b10011, 0b11001],         # x^4+x+1, x^4+x^3+1
    5:  [0b100101, 0b101001],       # x^5+x^2+1, x^5+x^3+1
    6:  [0b1000011, 0b1011011],     # x^6+x+1 dense; x^6+x^4+x^3+x+1
    7:  [0b10000011, 0b10001001],   # x^7+x+1; x^7+x^3+1
    8:  [0b100011011,               # x^8+x^4+x^3+x+1  (AES)
         0b100101011],              # x^8+x^5+x^3+x+1
    9:  [0b1000010001],             # x^9+x^4+1
    10: [0b10000001001],            # x^10+x^3+1
    11: [0b100000000101],           # x^11+x^2+1
    12: [0b1000000001111],          # x^12+x^3+x^2+x+1
    13: [0b10000000011011],
    14: [0b100000000101001],
    15: [0b1000000000110011],
    16: [0b10000000000101011,       # x^16+x^5+x^3+x+1
         0b10000000000010001],      # x^16+x^4+1 (trinomial extension)
}


def get_irreducible(m: int, index: int = 0) -> int:
    """Return a known irreducible polynomial of degree m (full bitmask)."""
    if m not in KNOWN_IRREDUCIBLES:
        raise ValueError(f"No hard-coded irreducible for degree {m}. Use find_irreducible().")
    polys = KNOWN_IRREDUCIBLES[m]
    return polys[index % len(polys)]


def find_irreducible(m: int, *, sparse_first: bool = True) -> int:
    """
    Find an irreducible polynomial of degree m by exhaustive search.

    Searches in order of Hamming weight (sparse first) if sparse_first=True,
    which tends to yield trinomials/pentanomials that reduce cheaply.
    Only feasible for m <= 20 or so.
    """
    if m in KNOWN_IRREDUCIBLES:
        return KNOWN_IRREDUCIBLES[m][0]

    base = 1 << m  # monic degree-m
    candidates = range(base + 1, base * 2, 2)  # odd (constant term 1)
    if sparse_first:
        candidates = sorted(candidates, key=lambda x: bin(x).count("1"))

    for c in candidates:
        if is_irreducible(c):
            return c
    raise RuntimeError(f"No irreducible polynomial found for degree {m}")


def lower_bits(poly_full: int) -> int:
    """Return the lower-m bits of a full irreducible (strip leading 1)."""
    m = degree(poly_full)
    return poly_full ^ (1 << m)


def sparsity(poly_full: int) -> int:
    """Number of nonzero coefficients (Hamming weight of the polynomial)."""
    return bin(poly_full).count("1")
