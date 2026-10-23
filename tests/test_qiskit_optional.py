import numpy as np
import pytest

qiskit = pytest.importorskip("qiskit")
from qiskit import QuantumCircuit  # noqa: E402

from quantum_workbench import simulate  # noqa: E402
from quantum_workbench.qiskit_adapter import from_qiskit, to_qiskit  # noqa: E402


def test_qiskit_import_and_backend_match():
    q = QuantumCircuit(3, 3)
    q.h(2)
    q.cx(2, 0)
    q.ry(.37, 1)
    q.measure([0, 1, 2], [0, 1, 2])
    circuit = from_qiskit(q)
    basic = simulate(circuit, backend="numpy")
    external = simulate(circuit, backend="qiskit")
    assert external.outcome_probabilities == pytest.approx(basic.outcome_probabilities,
                                                         abs=1e-10)


def test_qiskit_roundtrip_custom_gate():
    from qiskit.quantum_info import Operator

    q = QuantumCircuit(2)
    q.h(0)
    q.cp(.18, 0, 1)
    q.swap(0, 1)
    converted = from_qiskit(q)
    restored = to_qiskit(converted)
    np.testing.assert_allclose(Operator(q).data, Operator(restored).data, atol=1e-10)


def test_qiskit_rejects_unbound_parameters():
    from qiskit.circuit import Parameter

    from quantum_workbench.errors import UnsupportedOperationError

    q = QuantumCircuit(1)
    q.rx(Parameter("theta"), 0)
    with pytest.raises(UnsupportedOperationError, match="Bind"):
        from_qiskit(q)
