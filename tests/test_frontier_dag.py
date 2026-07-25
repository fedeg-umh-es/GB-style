from __future__ import annotations

import random

from gbext.fields import irreducible
from gbext.frontier.architectures import build_fus_dag, build_sep_dag
from gbext.poly import core


def _pad(values: list[int], length: int) -> list[int]:
    return values[:length] + [0] * max(0, length - len(values))


def _inputs(a: list[int], b: list[int]) -> dict[str, int]:
    return {
        **{f"a{i}": value for i, value in enumerate(a)},
        **{f"b{i}": value for i, value in enumerate(b)},
    }


def test_sep_binary_count_identity() -> None:
    m = 2
    p_full = irreducible.get_irreducible(m)
    g = [1, 1, 1]  # y^2 + y + 1 over GF(4)

    _, _, cost = build_sep_dag(g, p_full, m)

    assert cost.mul_var == 4
    assert cost.mul_const == 0
    assert cost.add == (2 - 1) ** 2 + 2 * (2 - 1)


def test_sep_and_fus_match_reference_exhaustively() -> None:
    m = 2
    k = 2
    p_full = irreducible.get_irreducible(m)
    g = [1, 2, 1]

    sep_dag, sep_outputs, sep_cost = build_sep_dag(g, p_full, m)
    fus_dag, fus_outputs, fus_cost = build_fus_dag(g, p_full, m)

    assert sep_cost.mul_var == fus_cost.mul_var == k * k

    vectors = [[x0, x1] for x0 in range(1 << m) for x1 in range(1 << m)]
    for a in vectors:
        for b in vectors:
            reference = _pad(core.reduce_mod(core.mul_schoolbook(a, b, p_full, m), g, p_full, m), k)
            assert sep_dag.evaluate(sep_outputs, _inputs(a, b), p_full, m) == reference
            assert fus_dag.evaluate(fus_outputs, _inputs(a, b), p_full, m) == reference


def test_random_nonbinary_modulus() -> None:
    m = 4
    k = 3
    p_full = irreducible.get_irreducible(m)
    g = [3, 0, 5, 1]
    rng = random.Random(0x47424653)

    sep_dag, sep_outputs, _ = build_sep_dag(g, p_full, m)
    fus_dag, fus_outputs, _ = build_fus_dag(g, p_full, m)

    for _ in range(100):
        a = [rng.randrange(1 << m) for _ in range(k)]
        b = [rng.randrange(1 << m) for _ in range(k)]
        reference = _pad(core.reduce_mod(core.mul_schoolbook(a, b, p_full, m), g, p_full, m), k)
        assert sep_dag.evaluate(sep_outputs, _inputs(a, b), p_full, m) == reference
        assert fus_dag.evaluate(fus_outputs, _inputs(a, b), p_full, m) == reference
