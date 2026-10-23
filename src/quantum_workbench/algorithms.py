"""Small teaching demonstrations for the v0.1 circuit and algorithm labs."""

from __future__ import annotations

import math

from quantum_workbench.circuits import Circuit


def bell() -> Circuit:
    return Circuit(2, 2, "Bell-state measurement").h(0).cx(0, 1).measure_all()


def ghz(num_qubits: int = 3) -> Circuit:
    if not 2 <= num_qubits <= 12:
        raise ValueError("GHZ teaching example requires 2-12 qubits")
    circuit = Circuit(num_qubits, num_qubits, f"GHZ-{num_qubits}")
    circuit.h(0)
    for qubit in range(1, num_qubits):
        circuit.cx(0, qubit)
    return circuit.measure_all()


def uniform(num_qubits: int = 7) -> Circuit:
    """Dense 2^n-outcome measurement distribution for histogram testing."""
    if not 1 <= num_qubits <= 12:
        raise ValueError("Uniform example requires 1-12 qubits")
    circuit = Circuit(num_qubits, num_qubits, f"Uniform-{num_qubits}")
    for qubit in range(num_qubits):
        circuit.h(qubit)
    return circuit.measure_all()


def measurement_demo() -> Circuit:
    """Create a Bell state, measure one qubit, then rotate the other.

    Demonstrates why the post-measurement state is conditional on the outcome.
    """
    return (Circuit(2, 1, "Mid-circuit measurement")
            .h(0).cx(0, 1).measure(0, 0).h(1))


def reset_demo() -> Circuit:
    """Reset an entangled qubit; the joint state becomes mixed."""
    return Circuit(2, name="Nonselective reset").h(0).cx(0, 1).reset(0)


def qft(num_qubits: int = 3, *, inverse: bool = False) -> Circuit:
    """QFT with output-bit reversal using Qiskit's little-endian convention."""
    if not 1 <= num_qubits <= 12:
        raise ValueError("QFT example requires 1-12 qubits")
    circuit = Circuit(num_qubits, name=f"{'Inverse ' if inverse else ''}QFT-{num_qubits}")
    if inverse:
        for i in range(num_qubits // 2):
            circuit.swap(i, num_qubits - 1 - i)
        for j in range(num_qubits):
            for m in range(j):
                circuit.cp(-math.pi / (2 ** (j - m)), m, j)
            circuit.h(j)
    else:
        for j in reversed(range(num_qubits)):
            circuit.h(j)
            for m in reversed(range(j)):
                circuit.cp(math.pi / (2 ** (j - m)), m, j)
        for i in range(num_qubits // 2):
            circuit.swap(i, num_qubits - 1 - i)
    return circuit


def qpe(precision: int = 3, phase: float = 0.125) -> Circuit:
    """QPE of U=P(2πθ) acting on known eigenstate |1>.

    This is an inspectable, *known-eigenstate* QPE demonstration, not general
    unitary synthesis or Shor modular exponentiation. The precision register
    is q[0]..q[precision-1]; readout string prints q[precision-1]..q[0].
    """
    if not 1 <= precision <= 8:
        raise ValueError("QPE example precision must be 1-8 bits")
    if not math.isfinite(phase) or not 0 <= phase < 1:
        raise ValueError("phase must be finite and in [0, 1)")
    target = precision
    circuit = Circuit(precision + 1, precision, f"QPE-{precision}bits-theta={phase:g}")
    circuit.x(target)
    for bit in range(precision):
        circuit.h(bit)
    for bit in range(precision):
        circuit.cp(2 * math.pi * phase * (2 ** bit), bit, target)
    circuit.append(qft(precision, inverse=True), range(precision), label="Inverse QFT")
    for bit in range(precision):
        circuit.measure(bit, bit)
    return circuit


EXAMPLES = {
    "bell": "Bell-state preparation and measurement",
    "ghz": "GHZ entanglement; works with seven or more wires",
    "uniform": "All 2^n computational outcomes equally likely; histogram stress case",
    "measurement": "Mid-circuit projective measurement with outcome branches",
    "reset": "Nonselective reset of one qubit of an entangled pair",
    "qft": "Quantum Fourier transform as composable gates",
    "inverse-qft": "Inverse Quantum Fourier transform",
    "qpe": "Quantum phase estimation of a known phase-gate eigenstate",
}


def make_example(name: str, *, num_qubits: int = 3, precision: int = 3,
                 phase: float = 0.125) -> Circuit:
    builders = {
        "bell": bell,
        "ghz": lambda: ghz(num_qubits),
        "uniform": lambda: uniform(num_qubits),
        "measurement": measurement_demo,
        "reset": reset_demo,
        "qft": lambda: qft(num_qubits),
        "inverse-qft": lambda: qft(num_qubits, inverse=True),
        "qpe": lambda: qpe(precision, phase),
    }
    if name not in builders:
        raise ValueError(f"Unknown example {name!r}; choices: {', '.join(EXAMPLES)}")
    return builders[name]()
