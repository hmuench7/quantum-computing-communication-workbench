# Conventions and semantics

## Qubit and bit ordering

`q[0]` is the **least significant** bit, as in Qiskit. A full basis label for three qubits is `q[2]q[1]q[0]`, so applying X to qubits 0 and 2 prepares `|101>`. `Circuit.cx(control, target)` has first argument the control. Multi-qubit unitary matrices follow the *local* little-endian order of their supplied qubit tuple: matrix basis `|q[k-1]...q[0]>`.

For `Step.distribution(qubits=[0,2])`, returned bitstrings are `q[2]q[0]`, not `q[0]q[2]`. A classical result prints classical bit `c[m-1]...c[0]`, including unmeasured bits initially set to zero.

## State and branches

The initial state is `|0...0>` times an optional overall global phase. A unitary gate evolves each conditional branch. Measurement uses exact Born-rule probabilities and **splits** each branch into feasible outcomes with normalized postmeasurement state. A reset is a measurement whose outcome is discarded and whose measured qubit is rotated to zero; it may leave the rest of the system mixed. `Branch.probability` is the probability of the complete measurement/reset history represented by that branch.

## Probability vs count

- **Exact probabilities:** computed from the weighted states and never estimated by finite shots.
- **Sampled counts:** a seeded multinomial sample of the final readout distribution with `shots` attempts; counts have statistical variation.
- **Final classical readout:** if the circuit contains classical bits, counts refer to these bits (not all unmeasured qubits).
- **Default final plot:** when classical bits exist, the default final histogram refers to the classical readout (important for QPE, whose target qubit is not measured). Select `qubits` explicitly for a quantum state marginal.
- **Selected-qubit marginal:** a user-selected subset of a quantum state at an inspection step, including the effects of any prior measurements or reset.
- **Top-k:** a view, not a change in the simulation. The 'Other' probability is the sum of *all* outcomes not shown; `--all` requests the complete outcome list.

## Deferred semantics

Measurement-conditioned classical gates, control-flow loops, general Kraus channels, photon loss, entanglement distribution over networks, QKD reconciliation, and quantum error correction are not available in the current simulator. Never replace these with identity operations or pretend an implementation exists.
