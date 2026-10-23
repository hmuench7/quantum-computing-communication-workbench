"""Create and simulate a custom three-qubit circuit; run from repository root."""

from quantum_workbench import Circuit, simulate
from quantum_workbench.export import save_result
from quantum_workbench.visualize import plot_probabilities

circuit = Circuit(3, 3, "Custom GHZ-like state")
subcircuit = Circuit(2, name="Entangle").h(0).cx(0, 1)
circuit.append(subcircuit, [0, 1], label="Bell preparation")
circuit.cx(1, 2)
circuit.measure_all()

result = simulate(circuit, shots=2000, seed=8)
print(result.summary())
save_result(result, "outputs/custom/trace.json")
plot_probabilities(result, path="outputs/custom/probabilities.png")
