import numpy as np
import pytest

from quantum_workbench import Circuit, simulate
from quantum_workbench.algorithms import bell, ghz


def test_bell_has_expected_amplitudes_and_correlations():
    result = simulate(bell(), shots=500, seed=13)
    premeasurement = result.steps[2].branches[0].amplitudes
    np.testing.assert_allclose(premeasurement, np.array([1, 0, 0, 1]) / np.sqrt(2))
    assert result.outcome_probabilities["00"] == pytest.approx(0.5)
    assert result.outcome_probabilities["11"] == pytest.approx(0.5)
    assert result.outcome_probabilities["01"] == pytest.approx(0)
    assert sum(result.counts.values()) == 500


def test_little_endian_basis_and_gate_target():
    result = simulate(Circuit(3).x(0).x(2))
    assert result.outcome_probabilities["101"] == pytest.approx(1)
    result2 = simulate(Circuit(2).x(0).cx(0, 1))
    assert result2.outcome_probabilities["11"] == pytest.approx(1)
    result3 = simulate(Circuit(2).x(1).cx(0, 1))
    assert result3.outcome_probabilities["10"] == pytest.approx(1)


def test_ghz_entangles_seven_wires():
    result = simulate(ghz(7))
    assert result.outcome_probabilities["0000000"] == pytest.approx(.5)
    assert result.outcome_probabilities["1111111"] == pytest.approx(.5)
    assert len(result.outcome_probabilities) == 128


def test_nonadjacent_custom_unitary_and_subcircuit():
    x = np.array([[0, 1], [1, 0]])
    block = Circuit(2, name="two x").x(0).x(1)
    c = Circuit(3).append(block, [0, 2]).unitary(x, [1], name="Custom-X")
    result = simulate(c)
    assert result.outcome_probabilities["111"] == pytest.approx(1)
    assert all(op.block == "two x" for op in c.operations[:2])


def test_reject_nonunitary_and_bad_qubits():
    with pytest.raises(ValueError, match="not unitary"):
        Circuit(1).unitary([[1, 1], [0, 1]], [0])
    with pytest.raises(ValueError, match="unique"):
        Circuit(2).cx(0, 0)
    with pytest.raises(ValueError, match="classical"):
        Circuit(1).measure(0, 0)


def test_parameterized_rotations_are_correct():
    c = Circuit(1).ry(np.pi, 0)
    assert simulate(c).outcome_probabilities["1"] == pytest.approx(1)
    c = Circuit(1).rx(np.pi / 2, 0)
    assert simulate(c).outcome_probabilities["1"] == pytest.approx(.5)
    c = Circuit(1).h(0).rz(np.pi, 0).h(0)
    assert simulate(c).outcome_probabilities["1"] == pytest.approx(1)


def test_measure_all_requires_enough_bits():
    with pytest.raises(ValueError, match="at least"):
        Circuit(2, 1).measure_all()


def test_qft_definition_matches_dft_sign():
    from quantum_workbench.algorithms import qft
    from quantum_workbench.backends import NumpyStateBackend

    n = 3
    source = np.eye(1 << n, dtype=complex)[1]
    for op in qft(n).operations:
        source = NumpyStateBackend().evolve(source, op.matrix, op.qubits, n)
    expected = np.exp(2j * np.pi * np.arange(1 << n) / (1 << n)) / np.sqrt(1 << n)
    np.testing.assert_allclose(source, expected, atol=1e-12)
