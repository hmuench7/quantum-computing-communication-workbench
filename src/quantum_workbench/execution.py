"""Exact small-circuit state tracing, nonselective reset, branching measurements.

Each measurement creates weighted conditional pure-state branches, rather than
silently treating the entire post-measurement system as a single pure state.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from quantum_workbench.backends import get_backend
from quantum_workbench.circuits import Circuit
from quantum_workbench.errors import ResourceLimitError, UnsupportedOperationError


@dataclass(frozen=True)
class Limits:
    max_qubits: int = 12
    max_operations: int = 512
    max_branches: int = 256
    max_snapshot_amplitudes: int = 2_000_000
    max_shots: int = 1_000_000


@dataclass(frozen=True)
class Branch:
    probability: float
    amplitudes: NDArray[np.complex128]
    classical_bits: tuple[int, ...]

    @property
    def classical_label(self) -> str:
        return "".join(str(b) for b in reversed(self.classical_bits))


@dataclass(frozen=True)
class Step:
    index: int
    operation: str
    qubits: tuple[int, ...]
    block: str | None
    branches: tuple[Branch, ...]
    num_qubits: int

    def distribution(self, qubits: Sequence[int] | None = None) -> dict[str, float]:
        """Exact probabilities in computational basis, optionally marginalized.

        The returned labels follow Qiskit ordering: the highest *selected local*
        bit prints at the left; ``qubits=(0, 2)`` produces labels q2 q0.
        """
        selected = tuple(range(self.num_qubits)) if qubits is None else tuple(qubits)
        if not selected or len(set(selected)) != len(selected) or any(
            not isinstance(q, int) or isinstance(q, bool) or not 0 <= q < self.num_qubits
            for q in selected
        ):
            raise ValueError("selected qubits must be distinct valid indices")
        indices = np.arange(1 << self.num_qubits, dtype=np.int64)
        reduced_indices = np.zeros(len(indices), dtype=np.int64)
        for position, qubit in enumerate(selected):
            reduced_indices |= ((indices >> qubit) & 1) << position
        probabilities = np.zeros(1 << len(selected), dtype=float)
        for branch in self.branches:
            probabilities += branch.probability * np.bincount(
                reduced_indices,
                weights=np.abs(branch.amplitudes) ** 2,
                minlength=1 << len(selected),
            )
        return {
            format(i, f"0{len(selected)}b"): float(p)
            for i, p in enumerate(probabilities)
        }

    def branch(self, index: int) -> Branch:
        return self.branches[index]


@dataclass(frozen=True)
class DistributionView:
    """Top-k summary; 'remaining_mass' is never silently dropped."""

    shown: tuple[tuple[str, float], ...]
    remaining_mass: float
    total_outcomes: int


def top_k(probabilities: dict[str, float], limit: int | None = 16) -> DistributionView:
    if limit is not None and limit < 1:
        raise ValueError("top_k must be positive or None")
    ordered = sorted(probabilities.items(), key=lambda item: (-item[1], item[0]))
    # Default views suppress zero/negligible numerical entries; --all exposes
    # the full basis and the remainder still accounts for every omitted value.
    visible = ordered if limit is None else [item for item in ordered if item[1] > 1e-12]
    picked = visible if limit is None else visible[:limit]
    return DistributionView(
        tuple(picked),
        float(sum(probability for _, probability in ordered[len(picked):])),
        len(probabilities),
    )


@dataclass(frozen=True)
class RunResult:
    circuit: Circuit
    steps: tuple[Step, ...]
    backend: str
    seed: int | None
    shots: int
    outcome_probabilities: dict[str, float]
    counts: dict[str, int]

    @property
    def final(self) -> Step:
        return self.steps[-1]

    def step(self, index: int) -> Step:
        return self.steps[index]

    @property
    def outcome_kind(self) -> str:
        return "classical-register" if self.circuit.num_clbits else "computational-basis"

    def summary(self, limit: int | None = 12) -> str:
        view = top_k(self.outcome_probabilities, limit)
        lines = [
            f"{self.circuit.name} | {self.circuit.num_qubits} qubits | "
            f"{len(self.circuit)} operations | {self.backend} backend",
            f"{self.shots} shots | {self.outcome_kind} | "
            f"{len(self.final.branches)} final branch(es)",
            "Outcome     Exact P       Count",
        ]
        for label, probability in view.shown:
            lines.append(f"{label:<11} {probability:>7.4f}     {self.counts.get(label, 0):>6}")
        if len(view.shown) != view.total_outcomes:
            lines.append(f"Other {view.total_outcomes - len(view.shown)} outcomes: "
                         f"P={view.remaining_mass:.6f}")
        return "\n".join(lines)


def _project(
    amplitudes: NDArray[np.complex128], qubit: int, outcome: int,
) -> tuple[float, NDArray[np.complex128]] | None:
    indices = np.arange(len(amplitudes))
    keep = ((indices >> qubit) & 1) == outcome
    prob = float(np.sum(np.abs(amplitudes[keep]) ** 2))
    if prob < 1e-14:
        return None
    projected = amplitudes.copy()
    projected[~keep] = 0
    projected /= np.sqrt(prob)
    return prob, projected


def _sample(probabilities: dict[str, float], shots: int, seed: int | None) -> dict[str, int]:
    keys = list(probabilities)
    weights = np.array([probabilities[key] for key in keys], dtype=float)
    weights /= weights.sum()
    counts = np.random.default_rng(seed).multinomial(shots, weights)
    return {key: int(count) for key, count in zip(keys, counts, strict=True) if count}


def simulate(
    circuit: Circuit,
    *,
    backend: str = "numpy",
    shots: int = 1024,
    seed: int | None = 42,
    limits: Limits | None = None,
) -> RunResult:
    """Simulate a supported circuit and record states after every operation.

    Terminal measurements sample from the corresponding classical register;
    with no classical register, samples from all qubits in Z basis. Mid-circuit
    measurement tracks both outcome probability and conditional post-state.
    Classical feedforward, channels and control-flow instructions are not
    modeled in this release.
    """
    limits = limits or Limits()
    if circuit.num_qubits > limits.max_qubits:
        raise ResourceLimitError(
            f"{circuit.num_qubits} qubits exceeds max_qubits={limits.max_qubits}; "
            "increase Limits deliberately if your memory permits"
        )
    if circuit.num_clbits > limits.max_qubits:
        raise ResourceLimitError("Classical register exceeds max_qubits limit for exact outcomes")
    if len(circuit) > limits.max_operations:
        raise ResourceLimitError("Circuit exceeds max_operations for dense traced simulation")
    if not isinstance(shots, int) or isinstance(shots, bool) or not 1 <= shots <= limits.max_shots:
        raise ValueError(f"shots must be an integer in [1, {limits.max_shots}]")
    engine = get_backend(backend)
    initial = np.zeros(1 << circuit.num_qubits, dtype=np.complex128)
    initial[0] = np.exp(1j * circuit.global_phase)
    branches = [Branch(1.0, initial, tuple(0 for _ in range(circuit.num_clbits)))]
    steps: list[Step] = []
    used_amplitudes = 0

    def capture(index: int, name: str, qubits: tuple[int, ...], block: str | None) -> None:
        nonlocal used_amplitudes
        needed = sum(len(branch.amplitudes) for branch in branches)
        if used_amplitudes + needed > limits.max_snapshot_amplitudes:
            raise ResourceLimitError(
                "Trace would exceed max_snapshot_amplitudes; reduce circuit length/"
                "qubits/measurement branches or adjust Limits"
            )
        used_amplitudes += needed
        steps.append(
            Step(
                index, name, qubits, block,
                tuple(
                    Branch(b.probability, b.amplitudes.copy(), b.classical_bits)
                    for b in branches
                ),
                circuit.num_qubits,
            )
        )

    capture(0, "INITIAL", (), None)
    for step_index, op in enumerate(circuit.operations, start=1):
        next_branches = []
        if op.name == "BARRIER":
            pass
        elif op.name == "MEASURE":
            assert op.clbit is not None
            for branch in branches:
                for outcome in (0, 1):
                    projection = _project(branch.amplitudes, op.qubits[0], outcome)
                    if projection is None:
                        continue
                    chance, state = projection
                    classical = list(branch.classical_bits)
                    classical[op.clbit] = outcome
                    next_branches.append(
                        Branch(branch.probability * chance, state, tuple(classical))
                    )
            branches = next_branches
        elif op.name == "RESET":
            # Trace out the measured environmental result: both possible
            # outcomes are retained as weighted conditional pure states.
            x = np.array([[0, 1], [1, 0]], dtype=np.complex128)
            for branch in branches:
                for outcome in (0, 1):
                    projection = _project(branch.amplitudes, op.qubits[0], outcome)
                    if projection is None:
                        continue
                    chance, state = projection
                    if outcome:
                        state = engine.evolve(state, x, op.qubits, circuit.num_qubits)
                    next_branches.append(
                        Branch(branch.probability * chance, state, branch.classical_bits)
                    )
            branches = next_branches
        elif op.matrix is not None:
            branches = [
                Branch(
                    b.probability,
                    engine.evolve(b.amplitudes, op.matrix, op.qubits, circuit.num_qubits),
                    b.classical_bits,
                )
                for b in branches
            ]
        else:
            raise UnsupportedOperationError(f"Unsupported operation {op.name!r}")
        if len(branches) > limits.max_branches:
            raise ResourceLimitError(
                f"Too many measurement/reset branches ({len(branches)}); "
                "reduce measurements or increase Limits.max_branches"
            )
        capture(step_index, op.name, op.qubits, op.block)

    if circuit.num_clbits:
        outcomes: dict[str, float] = {
            format(i, f"0{circuit.num_clbits}b"): 0.0 for i in range(1 << circuit.num_clbits)
        }
        for branch in branches:
            outcomes[branch.classical_label] += branch.probability
    else:
        outcomes = steps[-1].distribution()
    return RunResult(circuit, tuple(steps), engine.name, seed, shots, outcomes,
                     _sample(outcomes, shots, seed))
