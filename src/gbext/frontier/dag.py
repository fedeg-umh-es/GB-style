"""Minimal auditable DAG for exact GF(2^m)-operation counts.

The DAG counts operations in the outer coefficient field. It does not translate
those operations into binary gates. Fan-out is free. Identical operations are
not merged unless the caller explicitly reuses a node identifier.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from gbext.fields import gf2m


class Op(str, Enum):
    INPUT = "input"
    ZERO = "zero"
    ADD = "add"
    MUL_VAR = "mul_var"
    MUL_CONST = "mul_const"


@dataclass(frozen=True)
class Node:
    op: Op
    left: int | None = None
    right: int | None = None
    value: int | None = None
    name: str | None = None


class Dag:
    """Append-only arithmetic DAG with deterministic node identifiers."""

    def __init__(self) -> None:
        self.nodes: list[Node] = []
        self._zero = self._append(Node(Op.ZERO, value=0, name="0"))

    @property
    def zero(self) -> int:
        return self._zero

    def _append(self, node: Node) -> int:
        self.nodes.append(node)
        return len(self.nodes) - 1

    def input(self, name: str) -> int:
        return self._append(Node(Op.INPUT, name=name))

    def add(self, left: int, right: int) -> int:
        # Zero is structural identity and does not require a gate.
        if left == self.zero:
            return right
        if right == self.zero:
            return left
        return self._append(Node(Op.ADD, left=left, right=right))

    def mul_var(self, left: int, right: int) -> int:
        return self._append(Node(Op.MUL_VAR, left=left, right=right))

    def mul_const(self, signal: int, constant: int) -> int:
        if constant == 0:
            return self.zero
        if constant == 1:
            return signal
        return self._append(Node(Op.MUL_CONST, left=signal, value=constant))

    def sum_balanced(self, signals: Iterable[int]) -> int:
        level = [signal for signal in signals if signal != self.zero]
        if not level:
            return self.zero
        while len(level) > 1:
            next_level: list[int] = []
            for index in range(0, len(level), 2):
                if index + 1 == len(level):
                    next_level.append(level[index])
                else:
                    next_level.append(self.add(level[index], level[index + 1]))
            level = next_level
        return level[0]

    def counts(self) -> dict[str, int]:
        return {
            "mul_var": sum(node.op == Op.MUL_VAR for node in self.nodes),
            "mul_const": sum(node.op == Op.MUL_CONST for node in self.nodes),
            "add": sum(node.op == Op.ADD for node in self.nodes),
            "nodes": len(self.nodes),
        }

    def depth(self, outputs: Iterable[int]) -> int:
        memo: dict[int, int] = {}

        def visit(node_id: int) -> int:
            if node_id in memo:
                return memo[node_id]
            node = self.nodes[node_id]
            if node.op in {Op.INPUT, Op.ZERO}:
                result = 0
            elif node.op == Op.MUL_CONST:
                assert node.left is not None
                result = visit(node.left) + 1
            else:
                assert node.left is not None and node.right is not None
                result = max(visit(node.left), visit(node.right)) + 1
            memo[node_id] = result
            return result

        output_list = list(outputs)
        return max((visit(node_id) for node_id in output_list), default=0)

    def evaluate(
        self,
        outputs: Iterable[int],
        inputs: dict[str, int],
        p_full: int,
        m: int,
    ) -> list[int]:
        values: list[int] = [0] * len(self.nodes)
        for node_id, node in enumerate(self.nodes):
            if node.op == Op.ZERO:
                values[node_id] = 0
            elif node.op == Op.INPUT:
                if node.name not in inputs:
                    raise KeyError(f"Missing DAG input: {node.name}")
                values[node_id] = inputs[node.name]
            elif node.op == Op.ADD:
                assert node.left is not None and node.right is not None
                values[node_id] = values[node.left] ^ values[node.right]
            elif node.op == Op.MUL_VAR:
                assert node.left is not None and node.right is not None
                values[node_id] = gf2m.mul(values[node.left], values[node.right], p_full, m)
            elif node.op == Op.MUL_CONST:
                assert node.left is not None and node.value is not None
                values[node_id] = gf2m.mul(values[node.left], node.value, p_full, m)
            else:  # pragma: no cover
                raise ValueError(f"Unsupported operation: {node.op}")
        return [values[node_id] for node_id in outputs]
