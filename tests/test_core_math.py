import pytest
import numpy as np

from gbext.fields import gf2_poly
from gbext.fields import gf2m
from gbext.fields import irreducible
from gbext.poly import core
from gbext.gbstyle import linear_operator

def test_gf2_poly_arithmetic():
    assert gf2_poly.add(0b101, 0b011) == 0b110
    # (x^2+1)*(x+1) = x^3+x^2+x+1
    assert gf2_poly.mul(5, 3) == 15 

def test_irreducibility():
    assert gf2_poly.is_irreducible(0b111)  # x^2+x+1
    assert not gf2_poly.is_irreducible(0b1001)  # x^3+1 = (x+1)(x^2+x+1)
    
    m8_poly = irreducible.get_irreducible(8)
    assert gf2_poly.is_irreducible(m8_poly)

def test_gf2m_mul():
    p = 0b111 # x^2+x+1 (degree 2)
    m = 2
    
    # 2 = x, 3 = x+1. x*(x+1) = x^2+x
    # x^2+x mod x^2+x+1 = 1
    assert gf2m.mul(2, 3, p, m) == 1
    assert gf2m.mul_fast(2, 3, p, m) == 1
    assert gf2m.inv(2, p, m) == 3

def test_polynomial_arithmetic():
    p = 0b10011 # x^4+x+1
    m = 4
    
    a = [2, 3] # 2 + 3x
    b = [1, 2] # 1 + 2x
    
    # schoolbook
    # a*b = 2 + (4+3)x + 6x^2
    # in GF(2^4) with p=19:
    # 4(x^2) XOR 3(x+1) = x^2+x+1 (7)
    # 6(x^2+x)
    sb = core.mul_schoolbook(a, b, p, m)
    kar = core.mul_karatsuba(a, b, p, m, cutoff=1)
    
    assert sb == kar

def test_toeplitz_equivalence():
    p = 0b111
    m = 2
    k = 3
    a = [1, 2, 3]
    b = [2, 1, 3]
    
    T = linear_operator.build_toeplitz(a, k)
    tc = linear_operator.matmul_gf2m(T, b, p, m)
    
    cc = core.mul_schoolbook(a, b, p, m)
    while len(cc) < len(tc):
        cc.append(0)
        
    assert tc == cc

def test_reduction_equivalence():
    p = 0b111
    m = 2
    k = 3
    g = [1, 1, 1, 1] # x^3 + x^2 + x + 1
    
    R = linear_operator.build_reduction_matrix(g, k, p, m)
    
    # test a polynomial c of degree 2k-2 = 4
    c = [2, 1, 3, 2, 1]
    
    # Method 1: explicit matrix R * c
    red_mat = linear_operator.matmul_gf2m(R, c, p, m)
    
    # Method 2: procedural reduction
    red_proc = core.reduce_mod(c, g, p, m)
    while len(red_proc) < len(red_mat):
        red_proc.append(0)
        
    assert red_mat == red_proc
