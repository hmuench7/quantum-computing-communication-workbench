"""Import a Qiskit circuit and compare the two available unitary backends."""

from qiskit import QuantumCircuit

from quantum_workbench import simulate
from quantum_workbench.qiskit_adapter import from_qiskit, to_qiskit

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

circuit = from_qiskit(qc)
for engine in ("numpy", "qiskit"):
    result = simulate(circuit, backend=engine, shots=1000, seed=11)
    print(result.summary())

print("\nRound-tripped Qiskit circuit:")
print(to_qiskit(circuit).draw(output="text"))
