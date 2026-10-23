"""Optional Qiskit interoperability. No Qiskit dependency for the NumPy core."""

from __future__ import annotations

import numpy as np

from quantum_workbench.circuits import Circuit
from quantum_workbench.errors import UnsupportedOperationError


def from_qiskit(qiskit_circuit: object) -> Circuit:
    """Convert Qiskit QuantumCircuit gate-model circuits to our tracing IR.

    Supports unitary instructions representable by Operator, projective
    measurement, reset and barriers. Explicitly rejects control flow, delay,
    nonunitary channels and unbound parameters rather than silently skipping.
    """
    try:
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Operator
    except ImportError as exc:
        raise RuntimeError("Install Qiskit with: uv sync --extra qiskit") from exc
    if not isinstance(qiskit_circuit, QuantumCircuit):
        raise TypeError("Expected qiskit.QuantumCircuit")
    if qiskit_circuit.parameters:
        raise UnsupportedOperationError(
            "Bind all Qiskit circuit parameters before converting for simulation"
        )
    circuit = Circuit(qiskit_circuit.num_qubits, qiskit_circuit.num_clbits,
                      qiskit_circuit.name)
    circuit.global_phase = float(qiskit_circuit.global_phase)
    for item in qiskit_circuit.data:
        operation = item.operation
        qubits = tuple(qiskit_circuit.find_bit(q).index for q in item.qubits)
        clbits = tuple(qiskit_circuit.find_bit(c).index for c in item.clbits)
        name = operation.name.lower()
        if getattr(operation, "condition", None) is not None:
            raise UnsupportedOperationError(
                f"Instruction {operation.name} uses classical control (planned for v0.2+)"
            )
        if name == "measure":
            circuit.measure(qubits[0], clbits[0])
        elif name == "reset":
            circuit.reset(qubits[0])
        elif name == "barrier":
            circuit.barrier(*qubits)
        else:
            try:
                unitary = np.asarray(Operator(operation).data, dtype=np.complex128)
            except Exception as exc:
                raise UnsupportedOperationError(
                    f"Cannot convert {operation.name!r} to a unitary: {exc}"
                ) from exc
            circuit.unitary(unitary, qubits, name=operation.name.upper())
    return circuit


def to_qiskit(circuit: Circuit):
    """Export the supported circuit subset to a Qiskit QuantumCircuit."""
    try:
        from qiskit import QuantumCircuit
        from qiskit.circuit.library import UnitaryGate
    except ImportError as exc:
        raise RuntimeError("Install Qiskit with: uv sync --extra qiskit") from exc
    result = QuantumCircuit(circuit.num_qubits, circuit.num_clbits, name=circuit.name)
    result.global_phase = circuit.global_phase
    for operation in circuit.operations:
        if operation.name == "MEASURE":
            result.measure(operation.qubits[0], operation.clbit)
        elif operation.name == "RESET":
            result.reset(operation.qubits[0])
        elif operation.name == "BARRIER":
            result.barrier(*operation.qubits)
        elif operation.matrix is not None:
            result.append(UnitaryGate(operation.matrix, label=operation.name), operation.qubits)
        else:
            raise UnsupportedOperationError(f"Unknown operation: {operation.name}")
    return result
