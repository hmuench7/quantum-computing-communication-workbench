import numpy as np
import pytest

from quantum_workbench import simulate
from quantum_workbench.algorithms import qft, qpe
from quantum_workbench.backends import NumpyStateBackend


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_qft_followed_by_inverse_is_identity(n):
    engine = NumpyStateBackend()
    for basis in range(1 << n):
        state = np.eye(1 << n, dtype=complex)[basis]
        for op in qft(n).operations + qft(n, inverse=True).operations:
            state = engine.evolve(state, op.matrix, op.qubits, n)
        np.testing.assert_allclose(state, np.eye(1 << n)[basis], atol=1e-12)


@pytest.mark.parametrize("n,phase,label", [
    (3, 0.125, "001"), (3, 0.375, "011"),
    (4, 0.625, "1010"), (5, 0.0, "00000"),
])
def test_qpe_exact_eigenphases(n, phase, label):
    result = simulate(qpe(n, phase))
    assert result.outcome_probabilities[label] == pytest.approx(1, abs=1e-9)


def test_qpe_finite_precision_superposition_of_outcomes():
    result = simulate(qpe(3, .3))
    assert sum(result.outcome_probabilities.values()) == pytest.approx(1)
    assert result.outcome_probabilities["010"] > .5
    assert result.outcome_probabilities["011"] > .2


def test_composed_inverse_qft_block_is_visible_in_trace():
    result = simulate(qpe())
    assert any(step.block == "Inverse QFT" for step in result.steps)


def test_bad_phase_rejected():
    with pytest.raises(ValueError, match="phase"):
        qpe(3, 1.25)
