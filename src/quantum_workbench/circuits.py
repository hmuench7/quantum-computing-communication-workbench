"""A small backend-independent gate-model intermediate representation.

Qubit numbering is LITTLE-endian: qubit 0 is the least significant bit.
Unitary matrices use the local basis |q[k-1] ... q[0]>, where ``qubits``
lists local q[0], q[1], ... (also Qiskit's convention).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

ComplexMatrix = NDArray[np.complex128]

_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.diag([1, -1]).astype(complex)
_SWAP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)


def _controlled_matrix(u: ComplexMatrix) -> ComplexMatrix:
    """First local qubit is the control; second is the target."""
    matrix = np.eye(4, dtype=complex)
    for j in (0, 1):
        for k in (0, 1):
            matrix[1 + 2 * j, 1 + 2 * k] = u[j, k]
    return matrix


@dataclass(frozen=True)
class Operation:
    name: str
    qubits: tuple[int, ...]
    matrix: ComplexMatrix | None = field(default=None, repr=False, compare=False)
    clbit: int | None = None
    block: str | None = None
    parameters: tuple[float, ...] = ()


class Circuit:
    """Programmable unitary/measure/reset circuit, independent of a simulator.

    No classical feedforward or noise is claimed in v0.1. Arbitrary unitary
    matrices are supported within resource limits.
    """

    def __init__(self, num_qubits: int, num_clbits: int = 0, name: str = "Circuit") -> None:
        if not isinstance(num_qubits, int) or isinstance(num_qubits, bool) or num_qubits < 1:
            raise ValueError("num_qubits must be a positive integer")
        if not isinstance(num_clbits, int) or isinstance(num_clbits, bool) or num_clbits < 0:
            raise ValueError("num_clbits must be a nonnegative integer")
        self.num_qubits = num_qubits
        self.num_clbits = num_clbits
        self.name = name
        self.global_phase = 0.0
        self.operations: list[Operation] = []

    def _validate_qubits(self, qubits: Iterable[int]) -> tuple[int, ...]:
        qs = tuple(qubits)
        if not qs or len(set(qs)) != len(qs) or any(
            not isinstance(q, int) or isinstance(q, bool) or q < 0 or q >= self.num_qubits
            for q in qs
        ):
            raise ValueError(f"qubits must be unique indices in range(0, {self.num_qubits})")
        return qs

    def unitary(
        self, matrix: NDArray | list[list[complex]], qubits: Iterable[int], name: str = "U",
        block: str | None = None, parameters: tuple[float, ...] = (),
    ) -> Circuit:
        qs = self._validate_qubits(qubits)
        # Limit the input size before allocating expensive validation products.
        if len(qs) > 8:
            raise ValueError("Custom matrix gates are limited to 8 qubits in v0.1")
        u = np.asarray(matrix, dtype=np.complex128)
        width = 1 << len(qs)
        if u.shape != (width, width) or not np.isfinite(u).all():
            raise ValueError(f"{name}: expected a finite {width}x{width} complex matrix")
        if not np.allclose(u.conj().T @ u, np.eye(width), atol=1e-9, rtol=1e-9):
            raise ValueError(f"{name}: matrix is not unitary")
        self.operations.append(Operation(name, qs, u.copy(), block=block, parameters=parameters))
        return self

    def h(self, q: int) -> Circuit:
        return self.unitary(_H, [q], "H")

    def x(self, q: int) -> Circuit:
        return self.unitary(_X, [q], "X")

    def y(self, q: int) -> Circuit:
        return self.unitary(_Y, [q], "Y")

    def z(self, q: int) -> Circuit:
        return self.unitary(_Z, [q], "Z")

    def s(self, q: int) -> Circuit:
        return self.p(np.pi / 2, q, name="S")

    def t(self, q: int) -> Circuit:
        return self.p(np.pi / 4, q, name="T")

    def p(self, theta: float, q: int, name: str = "P") -> Circuit:
        return self.unitary(np.diag([1, np.exp(1j * theta)]), [q], name,
                            parameters=(float(theta),))

    def rx(self, theta: float, q: int) -> Circuit:
        return self.unitary(
            np.cos(theta / 2) * np.eye(2) - 1j * np.sin(theta / 2) * _X,
            [q], "RX", parameters=(float(theta),),
        )

    def ry(self, theta: float, q: int) -> Circuit:
        return self.unitary(
            np.cos(theta / 2) * np.eye(2) - 1j * np.sin(theta / 2) * _Y,
            [q], "RY", parameters=(float(theta),),
        )

    def rz(self, theta: float, q: int) -> Circuit:
        return self.unitary(
            np.cos(theta / 2) * np.eye(2) - 1j * np.sin(theta / 2) * _Z,
            [q], "RZ", parameters=(float(theta),),
        )

    def cx(self, control: int, target: int) -> Circuit:
        return self.unitary(_controlled_matrix(_X), [control, target], "CX")

    def cy(self, control: int, target: int) -> Circuit:
        return self.unitary(_controlled_matrix(_Y), [control, target], "CY")

    def cz(self, a: int, b: int) -> Circuit:
        return self.unitary(np.diag([1, 1, 1, -1]), [a, b], "CZ")

    def cp(self, theta: float, control: int, target: int) -> Circuit:
        return self.unitary(
            np.diag([1, 1, 1, np.exp(1j * theta)]), [control, target], "CP",
            parameters=(float(theta),),
        )

    def swap(self, a: int, b: int) -> Circuit:
        return self.unitary(_SWAP, [a, b], "SWAP")

    def measure(self, qubit: int, clbit: int) -> Circuit:
        self._validate_qubits([qubit])
        if (
            not isinstance(clbit, int) or isinstance(clbit, bool)
            or not 0 <= clbit < self.num_clbits
        ):
            raise ValueError("measurement requires an existing classical bit")
        self.operations.append(Operation("MEASURE", (qubit,), clbit=clbit))
        return self

    def measure_all(self) -> Circuit:
        if self.num_clbits < self.num_qubits:
            raise ValueError("measure_all requires at least as many classical bits as qubits")
        for qubit in range(self.num_qubits):
            self.measure(qubit, qubit)
        return self

    def reset(self, qubit: int) -> Circuit:
        self._validate_qubits([qubit])
        self.operations.append(Operation("RESET", (qubit,)))
        return self

    def barrier(self, *qubits: int) -> Circuit:
        self.operations.append(
            Operation("BARRIER", self._validate_qubits(qubits or range(self.num_qubits)))
        )
        return self

    def append(self, other: Circuit, qubits: Iterable[int], *, label: str | None = None) -> Circuit:
        """Inline a unitary subcircuit with a visible logical block label.

        ``other`` must not contain measurements/reset or classical bits; those
        operations require explicit classical-register mapping in later releases.
        """
        qs = self._validate_qubits(qubits)
        if len(qs) != other.num_qubits or other.num_clbits:
            raise ValueError("Subcircuit qubit count must match and cannot have classical bits")
        if any(op.matrix is None for op in other.operations):
            raise ValueError("Only purely unitary subcircuits can be composed in v0.1")
        block = label or other.name
        for op in other.operations:
            self.operations.append(
                Operation(op.name, tuple(qs[i] for i in op.qubits), op.matrix,
                          block=block, parameters=op.parameters)
            )
        self.global_phase += other.global_phase
        return self

    def __len__(self) -> int:
        return len(self.operations)
