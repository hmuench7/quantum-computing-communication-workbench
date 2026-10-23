import numpy as np
import pytest

from quantum_workbench import Circuit, Limits, simulate, top_k
from quantum_workbench.algorithms import measurement_demo, reset_demo, uniform
from quantum_workbench.errors import ResourceLimitError


def test_measurement_branches_record_conditional_state():
    result = simulate(measurement_demo())
    stage = result.steps[3]
    assert stage.operation == "MEASURE"
    assert len(stage.branches) == 2
    assert [b.classical_label for b in stage.branches] == ["0", "1"]
    assert [b.probability for b in stage.branches] == pytest.approx([.5, .5])
    np.testing.assert_allclose(stage.branches[0].amplitudes, [1, 0, 0, 0])
    np.testing.assert_allclose(stage.branches[1].amplitudes, [0, 0, 0, 1])
    # Subsequent H on q1 transforms the two branches independently.
    assert len(result.final.branches) == 2
    assert result.final.distribution([1]) == pytest.approx({"0": .5, "1": .5})


def test_reset_is_not_falsely_pure():
    result = simulate(reset_demo())
    assert len(result.final.branches) == 2
    assert result.final.distribution() == pytest.approx({"00": .5, "10": .5,
                                                       "01": 0, "11": 0})
    assert all(abs(b.amplitudes[1]) < 1e-12 for b in result.final.branches)


def test_measurement_overwrites_classical_bit():
    circuit = Circuit(1, 1).h(0).measure(0, 0).x(0).measure(0, 0)
    result = simulate(circuit)
    assert result.outcome_probabilities == pytest.approx({"0": .5, "1": .5})


def test_dense_seven_bit_histogram_and_aggregate_mass():
    result = simulate(uniform(7), seed=41)
    probs = result.outcome_probabilities
    assert len(probs) == 128
    assert all(p == pytest.approx(1 / 128) for p in probs.values())
    shown = top_k(probs, 16)
    assert shown.total_outcomes == 128
    assert len(shown.shown) == 16
    assert shown.remaining_mass == pytest.approx(112 / 128)
    assert sum(result.counts.values()) == 1024
    assert result.counts == simulate(uniform(7), seed=41).counts


def test_partial_quantum_marginal_not_classical_distribution():
    result = simulate(Circuit(3).h(0).x(2))
    assert result.final.distribution([0, 2]) == pytest.approx(
        {"00": 0, "01": 0, "10": .5, "11": .5}
    )


def test_guard_large_circuits_and_branch_explosion():
    with pytest.raises(ResourceLimitError, match="max_qubits"):
        simulate(Circuit(13))
    with pytest.raises(ResourceLimitError, match="Too many"):
        simulate(uniform(7), limits=Limits(max_branches=16))
    with pytest.raises(ResourceLimitError, match="snapshot"):
        simulate(Circuit(4).h(0), limits=Limits(max_snapshot_amplitudes=16))
    with pytest.raises(ValueError, match="shots"):
        simulate(Circuit(1), shots=0)


def test_global_phase_is_preserved_in_amplitudes():
    circuit = Circuit(1).x(0)
    circuit.global_phase = np.pi / 2
    state = simulate(circuit).final.branches[0].amplitudes
    np.testing.assert_allclose(state, [0, 1j], atol=1e-12)


def test_memory_snapshot_remains_immutable_after_later_gates():
    result = simulate(Circuit(1).h(0).h(0))
    np.testing.assert_allclose(result.steps[1].branches[0].amplitudes,
                               [1 / np.sqrt(2), 1 / np.sqrt(2)])
    np.testing.assert_allclose(result.steps[2].branches[0].amplitudes, [1, 0], atol=1e-12)
