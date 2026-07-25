"""Model-matched SEP and diagnostic FUS architectures.

Both builders use the same outer-field operation model:
- one variable-variable multiplication per coefficient product;
- one addition per explicit binary sum node;
- one constant multiplication per explicitly constructed scalar multiple;
- free fan-out;
- no global CSE or algebraic rewriting.

FUS is a diagnostic independent-output realization. It is not identified with
Mastrovito or TMVP from the literature.
"""

from __future__ import annotations

from dataclasses import dataclass

from gbext.frontier.dag import Dag
from gbext.gbstyle.linear_operator import build_reduction_matrix


@dataclass(frozen=True)
class ArchitectureCost:
    architecture: str
    mul_var: int
    mul_const: int
    add: int
    depth: int
    nodes: int

    @classmethod
    def from_dag(cls, architecture: str, dag: Dag, outputs: list[int]) -> "ArchitectureCost":
        counts = dag.counts()
        return cls(
            architecture=architecture,
            mul_var=counts["mul_var"],
            mul_const=counts["mul_const"],
            add=counts["add"],
            depth=dag.depth(outputs),
            nodes=counts["nodes"],
        )


def _inputs_and_products(dag: Dag, k: int) -> tuple[list[int], list[int], list[list[int]]]:
    a_nodes = [dag.input(f"a{index}") for index in range(k)]
    b_nodes = [dag.input(f"b{index}") for index in range(k)]
    products = [
        [dag.mul_var(a_nodes[i], b_nodes[j]) for j in range(k)]
        for i in range(k)
    ]
    return a_nodes, b_nodes, products


def build_sep_dag(g: list[int], p_full: int, m: int) -> tuple[Dag, list[int], ArchitectureCost]:
    """Build separated convolution followed by descending fixed reduction."""
    k = len(g) - 1
    if k < 1 or g[-1] != 1:
        raise ValueError("g must be monic and have positive degree")

    dag = Dag()
    _, _, products = _inputs_and_products(dag, k)

    coefficients: list[int] = []
    for degree in range(2 * k - 1):
        diagonal = [products[i][degree - i] for i in range(k) if 0 <= degree - i < k]
        coefficients.append(dag.sum_balanced(diagonal))

    state = coefficients.copy()
    lower_support = [(exponent, coefficient) for exponent, coefficient in enumerate(g[:-1]) if coefficient]

    for degree in range(2 * k - 2, k - 1, -1):
        high_signal = state[degree]
        # Sharing rule: the same scalar multiple of the same high signal is
        # constructed once and may fan out to all taps carrying that constant.
        scaled_by_constant: dict[int, int] = {}
        for exponent, coefficient in lower_support:
            if coefficient not in scaled_by_constant:
                scaled_by_constant[coefficient] = dag.mul_const(high_signal, coefficient)
            destination = degree - k + exponent
            state[destination] = dag.add(state[destination], scaled_by_constant[coefficient])

    outputs = state[:k]
    return dag, outputs, ArchitectureCost.from_dag("SEP_SB", dag, outputs)


def build_fus_dag(g: list[int], p_full: int, m: int) -> tuple[Dag, list[int], ArchitectureCost]:
    """Build a canonical fused realization with independent output sums.

    Each product a_i*b_j is created once. For a fixed product and a fixed
    non-unit reduction coefficient, the scalar multiple is created once and
    may fan out to several outputs. XOR/add nodes are not shared across outputs.
    """
    k = len(g) - 1
    if k < 1 or g[-1] != 1:
        raise ValueError("g must be monic and have positive degree")

    dag = Dag()
    _, _, products = _inputs_and_products(dag, k)
    reduction = build_reduction_matrix(g, k, p_full, m)
    output_terms: list[list[int]] = [[] for _ in range(k)]
    scaled_cache: dict[tuple[int, int, int], int] = {}

    for i in range(k):
        for j in range(k):
            product = products[i][j]
            degree = i + j
            for output_index in range(k):
                coefficient = reduction[output_index][degree]
                if coefficient == 0:
                    continue
                key = (i, j, coefficient)
                if key not in scaled_cache:
                    scaled_cache[key] = dag.mul_const(product, coefficient)
                output_terms[output_index].append(scaled_cache[key])

    outputs = [dag.sum_balanced(terms) for terms in output_terms]
    return dag, outputs, ArchitectureCost.from_dag("FUS_CAN", dag, outputs)


def weighted_delta(
    sep: ArchitectureCost,
    fus: ArchitectureCost,
    rho_var: float,
    rho_const: float,
) -> float:
    """Return C(SEP)-C(FUS) under a declared weighted operation model."""
    sep_cost = rho_var * sep.mul_var + rho_const * sep.mul_const + sep.add
    fus_cost = rho_var * fus.mul_var + rho_const * fus.mul_const + fus.add
    return sep_cost - fus_cost


def constant_break_even(sep: ArchitectureCost, fus: ArchitectureCost) -> float | None:
    """Solve delta_A + rho_const*delta_Mc = 0 when variable counts match."""
    if sep.mul_var != fus.mul_var:
        return None
    delta_mc = sep.mul_const - fus.mul_const
    delta_add = sep.add - fus.add
    if delta_mc == 0:
        return None
    return -delta_add / delta_mc
