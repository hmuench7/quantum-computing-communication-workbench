"""Regression checks for v0.1 manual-acceptance follow-up examples."""

import numpy as np
import pytest

from quantum_workbench import simulate
from quantum_workbench.algorithms import bell, uniform
from quantum_workbench.errors import UnsupportedOperationError
from quantum_workbench.export import result_dict


def test_amplitude_export_has_normalized_branch_vectors():
    for circuit in (bell(), uniform(7)):
        result = simulate(circuit)
        compact = result_dict(result)
        expanded = result_dict(result, include_amplitudes=True)
        assert compact["outcomes"] == expanded["outcomes"]
        for step in expanded["steps"]:
            assert sum(b["probability"] for b in step["branches"]) == pytest.approx(1.0)
            for branch in step["branches"]:
                array = np.asarray(branch["amplitudes"], dtype=float)
                assert array.shape == (1 << circuit.num_qubits, 2)
                assert np.sum(array**2) == pytest.approx(1.0)


def test_qiskit_custom_unitary_gate_import():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import UnitaryGate
    from qiskit.quantum_info import Statevector

    from quantum_workbench.qiskit_adapter import from_qiskit

    qc = QuantumCircuit(2)
    qc.append(UnitaryGate(np.array([[0, 1], [1, 0]], dtype=complex)), [1])
    qc.h(0)
    qc.cx(0, 1)
    actual = simulate(from_qiskit(qc)).final.branches[0].amplitudes
    expected = Statevector.from_instruction(qc).data
    np.testing.assert_allclose(actual, expected, atol=1e-10)


def test_qiskit_composed_gate_import():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    from quantum_workbench.qiskit_adapter import from_qiskit

    block = QuantumCircuit(2)
    block.h(0)
    block.cx(0, 1)
    qc = QuantumCircuit(2)
    qc.append(block.to_gate(label="Bell"), [0, 1])
    converted = from_qiskit(qc)
    assert len(converted.operations) == 1
    actual = simulate(converted).final.branches[0].amplitudes
    expected = Statevector.from_instruction(qc).data
    np.testing.assert_allclose(actual, expected, atol=1e-10)


def test_qiskit_dynamic_if_test_rejected_explicitly():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit

    from quantum_workbench.qiskit_adapter import from_qiskit

    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    with qc.if_test((qc.clbits[0], 1)):
        qc.x(0)
    with pytest.raises(UnsupportedOperationError, match="classical control flow 'if_else'"):
        from_qiskit(qc)
