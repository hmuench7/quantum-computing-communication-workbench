"""Pluggable pure-state unitary backends.

The NumPy implementation acts as an independently testable baseline. Qiskit
provides an optional adapter that uses its established Statevector.evolve API.
Branching, measurement and reset are shared orchestration code in execution.py.
"""

from __future__ import annotations

from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from quantum_workbench.circuits import ComplexMatrix


class StateBackend(Protocol):
    name: str

    def evolve(
        self, state: NDArray[np.complex128], unitary: ComplexMatrix,
        qubits: tuple[int, ...], num_qubits: int,
    ) -> NDArray[np.complex128]: ...


class NumpyStateBackend:
    name = "numpy"

    def evolve(
        self, state: NDArray[np.complex128], unitary: ComplexMatrix,
        qubits: tuple[int, ...], num_qubits: int,
    ) -> NDArray[np.complex128]:
        # Tensor axes run from q[n-1] (leftmost) to q[0] (rightmost).
        # Local matrix axes run from the highest numbered *local* qubit to lowest.
        targets = [num_qubits - 1 - q for q in reversed(qubits)]
        untouched = [axis for axis in range(num_qubits) if axis not in targets]
        perm = targets + untouched
        tensor = state.reshape([2] * num_qubits).transpose(perm)
        transformed = unitary @ tensor.reshape(1 << len(qubits), -1)
        return np.asarray(
            transformed.reshape([2] * num_qubits).transpose(np.argsort(perm)).reshape(-1),
            dtype=np.complex128,
        )


class QiskitStateBackend:
    name = "qiskit"

    def __init__(self) -> None:
        try:
            from qiskit.quantum_info import Operator, Statevector
        except ImportError as exc:
            raise RuntimeError(
                "Qiskit backend requires optional dependencies: uv sync --extra qiskit"
            ) from exc
        self._operator = Operator
        self._statevector = Statevector

    def evolve(
        self, state: NDArray[np.complex128], unitary: ComplexMatrix,
        qubits: tuple[int, ...], num_qubits: int,
    ) -> NDArray[np.complex128]:
        evolved = self._statevector(state).evolve(self._operator(unitary), qargs=list(qubits))
        return np.asarray(evolved.data, dtype=np.complex128)


def get_backend(name: str) -> StateBackend:
    if name == "numpy":
        return NumpyStateBackend()
    if name == "qiskit":
        return QiskitStateBackend()
    raise ValueError(f"Unknown backend {name!r}; choose 'numpy' or 'qiskit'")
