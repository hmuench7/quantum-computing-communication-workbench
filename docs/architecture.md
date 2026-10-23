# v0.1 engineering architecture

**Status:** implemented where explicitly indicated; 2026-10-22. Product roadmap: [`design/product-requirements-v0.2.md`](design/product-requirements-v0.2.md).

## System boundaries

```
User Python code / CLI / optional Qiskit QuantumCircuit
                     |
             Circuit / Operation IR
                     |
     Exact branch/measurement/reset tracer
                     |
       unitary backend protocol (StateBackend)
           /                     \
  NumPy reference backend      Qiskit Statevector backend (optional)
                     |
         Result / Step / Branch objects
                     |
   JSON exports / static charts / CLI inspection
```

This is a **small local library**. It deliberately does not contain an HTTP server, arbitrary Python-code upload endpoint, frontend, QKD protocol simulator, QEC decoder, or generic noise engine.

## Architectural decisions (ADR-001 through ADR-007)

1. **Backend-independent intermediate representation.** Circuit stores a small validated list of unitary / measurement / reset / barrier operations. Qiskit import/export is optional. This is not a general replacement for Qiskit, OpenQASM, or arbitrary quantum hardware instructions.
2. **NumPy reference engine remains available without Qiskit.** A small tested tensor-axis evolution formula applies finite-size matrix gates to sparse sets of qubits. It supplies a local, reproducible baseline and enables tests without a Qiskit installation. Qiskit's `Statevector.evolve(Operator, qargs=...)` is the optional established reference to compare. Neither is intended as a high-performance simulator.
3. **Exact measurement branches.** Each projective Z measurement records both conditional normalized states and Born probabilities. Subsequent gates evolve each branch separately. Repeated shots sample from exact final classical bit distributions rather than falsely running the trace as one state.
4. **Reset is not a projection onto one fabricated pure state.** Nonselective reset branches are preserved, keeping correct mixed-state *probabilities* even though v0.1 has no explicit density-matrix UI.
5. **No fabricated classical control.** Dynamic `if_test`/`if_else`, measurement-conditioned gates, and opaque nonunitary operations are rejected by the Qiskit importer. In a later version, a classical-control interpreter or Aer-based trace adapter will implement them correctly.
6. **Adaptive visual summaries.** Displays default to the most significant outcomes and explicitly report the probability not shown. A requested marginal is evaluated over the *specified quantum qubits*; sampled outcome counts are over measured classical registers. These are separate APIs.
7. **Local-first UI path.** `RunResult` is the future local web API boundary. The JSON schema intentionally contains only data. A later frontend should visualize it without executing Python. Current static plots are useful visual regression fixtures, not the final UI.

## Public API and contracts

- `Circuit(num_qubits, num_clbits, name)`, gate methods, `unitary(matrix, qubits)`, `append(subcircuit, qubits)`, `measure`, `reset`, `barrier`.
- `simulate(circuit, backend='numpy', seed=42, shots=1024, limits=Limits()) -> RunResult`.
- `RunResult.steps[step].branches[branch]`: probability, classical bits, conditional amplitudes.
- `Step.distribution(qubits=None)`: exact computational-basis probability distribution. Marginal qubit ordering is described in `docs/conventions.md`.
- `RunResult.outcome_probabilities`, `.counts`: final classical result probability/sampled counts when classical bits are present; otherwise a final computational-basis measurement of all qubits.
- `quantum_workbench.qiskit_adapter.from_qiskit/to_qiskit`: supported Qiskit circuit interoperability.
- `plot_circuit`, `plot_probabilities`, `save_result`.

## Algorithms and example coverage

- Bell / GHZ: state preparation and correlations.
- Uniform: 2^n nonzero readout outcomes, demonstrates seven-bit and higher histograms.
- QFT/inverse QFT: gate-composed implementations; group metadata preserved on append.
- QPE: controlled powers of a phase gate on a **known** eigenstate |1>; exact and finite-precision examples. No generic modular-exponentiation oracle.
- Mid-measurement and reset: exact branches; illustrates destructive measurement and entanglement loss.

## Resource and correctness limitations

The dense state has 2^n complex amplitudes, 16 bytes per amplitude (complex128) excluding arrays/intermediate overhead. Per-step tracing costs O(steps × branches × 2^n) memory. Default limits: max_qubits=12, max_operations=512, max_branches=256, max_snapshot_amplitudes=2,000,000, max_shots=1,000,000. Users can change these deliberately with `Limits`; increasing settings does **not** make general-purpose 30+ qubit simulation tractable.

Exact classical outcome dictionaries also require up to 2^m labels for m classical bits, so v0.1 restricts register size to the qubit limit. Tiny probabilities below 1e-14 in projection may be treated as numerical zeros; normalized sum should be 1 within floating-point tolerance, not assumed exactly 1.

Potential follow-up before supporting larger registers: sparse counts/distributions, mixed-state compaction, collapse branches with identical classical and quantum states, state checkpoint selection, branch-aware GUI, frontend virtualized plots, streaming saves.

## Dependency rationale

- **NumPy:** small-state tensor operations and sampling; a reference/fallback backend.
- **Matplotlib:** figure export and comparison to expected histograms; no mandatory notebook environment.
- **Qiskit (optional):** established quantum circuit representations and `Statevector.evolve`; import/export and independent comparison, within declared adapter limitations.
- **pytest and Ruff (dev):** repeatable correctness/style gates.
- **hatchling and uv:** PEP 517 package build and local dependency management.

Aer is **not** installed: noise and accelerated sampling are later modules, and the Aer repository has announced reduced maintenance. Qiskit circuit interoperability should not depend on Aer.

## Evolution of the architecture

- v0.2: FastAPI read-only local-service layer, React/TypeScript UI, circuit block hierarchy, state inspector, branch switcher, selected-register histograms. Browser UI must never execute arbitrary shared Python snippets.
- v0.3+: dedicated algorithm module (including toy order-finding), quantum/classical protocol event engine (BB84), noise channels.
- Later: QEC backend interface and Stim/PyMatching integration; high-level photonic/network simulator where scientifically justified.
