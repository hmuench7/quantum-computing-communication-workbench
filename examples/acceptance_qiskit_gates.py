"""Acceptance example: Qiskit custom UnitaryGate and composed to_gate().

Run from repository root:
    uv run python examples/acceptance_qiskit_gates.py
Requires optional Qiskit extra: uv sync --extra dev --extra qiskit
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import UnitaryGate
from qiskit.quantum_info import Statevector

from quantum_workbench import simulate
from quantum_workbench.qiskit_adapter import from_qiskit, to_qiskit


# Case A: a hand-defined unitary on q1. After H(q0) + CX(q0,q1),
# the state is (|01> + |10>)/sqrt(2).
def custom_unitary_case() -> tuple[QuantumCircuit, QuantumCircuit, dict[str, float]]:
    unitary_part = QuantumCircuit(2, name="Custom X then entangle")
    custom_x = UnitaryGate(np.array([[0, 1], [1, 0]], dtype=complex), label="My X")
    unitary_part.append(custom_x, [1])
    unitary_part.h(0)
    unitary_part.cx(0, 1)
    measured = QuantumCircuit(2, 2, name="Custom unitary acceptance")
    measured.compose(unitary_part, inplace=True)
    measured.measure([0, 1], [0, 1])
    return unitary_part, measured, {"01": 0.5, "10": 0.5}


# Case B: construct a two-qubit Bell preparation as a composed Qiskit gate.
# This is one logical operation in the imported v0.1 trace, not two substeps.
def composed_gate_case() -> tuple[QuantumCircuit, QuantumCircuit, dict[str, float]]:
    bell_block = QuantumCircuit(2, name="Bell preparation")
    bell_block.h(0)
    bell_block.cx(0, 1)
    unitary_part = QuantumCircuit(2, name="Composed Bell gate")
    unitary_part.append(bell_block.to_gate(label="Bell block"), [0, 1])
    measured = QuantumCircuit(2, 2, name="Composite gate acceptance")
    measured.compose(unitary_part, inplace=True)
    measured.measure([0, 1], [0, 1])
    return unitary_part, measured, {"00": 0.5, "11": 0.5}


def check_case(
    title: str,
    unitary_part: QuantumCircuit,
    measured: QuantumCircuit,
    expected: dict[str, float],
) -> None:
    print(f"\n=== {title} ===")
    print(measured.draw(output="text"))
    converted = from_qiskit(measured)
    reference = Statevector.from_instruction(unitary_part).data

    for backend in ("numpy", "qiskit"):
        state_run = simulate(from_qiskit(unitary_part), backend=backend, shots=1024, seed=21)
        actual_state = state_run.final.branches[0].amplitudes
        np.testing.assert_allclose(actual_state, reference, atol=1e-10, rtol=0)
        measured_run = simulate(converted, backend=backend, shots=1024, seed=21)
        for bitstring, probability in measured_run.outcome_probabilities.items():
            np.testing.assert_allclose(probability, expected.get(bitstring, 0), atol=1e-10)
        print(f"{backend}: {measured_run.outcome_probabilities}")

    # Verify that the supported subset can be exported back to Qiskit.
    imported_unitary = from_qiskit(unitary_part)
    roundtripped = to_qiskit(imported_unitary)
    roundtrip_state = Statevector.from_instruction(roundtripped).data
    np.testing.assert_allclose(roundtrip_state, reference, atol=1e-10, rtol=0)
    print("PASS: both engines, expected outcomes, and Qiskit round trip")
    print("Imported operation names:", [op.name for op in converted.operations])


def main() -> None:
    check_case("Custom UnitaryGate", *custom_unitary_case())
    check_case("Composed gate via to_gate()", *composed_gate_case())
    print("\nAll Qiskit gate interoperability checks passed.")


if __name__ == "__main__":
    main()
