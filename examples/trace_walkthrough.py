"""Inspect the post-measurement branches and the probabilities after each step."""

from quantum_workbench import measurement_demo, simulate

result = simulate(measurement_demo())
for step in result.steps:
    print(f"\nStep {step.index}: {step.operation}, branches={len(step.branches)}")
    for i, branch in enumerate(step.branches):
        supported = [
            (format(basis, f"0{step.num_qubits}b"), complex(amplitude))
            for basis, amplitude in enumerate(branch.amplitudes)
            if abs(amplitude) > 1e-10
        ]
        print(f"  Branch {i}: P={branch.probability:.3f}, "
              f"classical={branch.classical_label or '(none)'}, state={supported}")
