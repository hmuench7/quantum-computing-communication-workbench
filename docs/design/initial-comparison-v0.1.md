# Quantum Circuit Explorer — Requirements, Ecosystem Review, and Roadmap

**Document version:** 0.1 (design proposal)  
**Research date:** 2026-10-22  
**Decision status:** Proposed — favor existing simulator plus custom educational interface  
**Initial scope:** Qubit-based, gate-model quantum circuits; local-first, Python-programmable

## Executive decision

**Recommended option:** Start by using IBM Quantum Composer and Quirk-E for immediate educational demonstrations; build a differentiated open-source application only if students need first-class inspection of measurement-conditioned state evolution, a programmable lesson library, exact branch probabilities, and a consistent local workflow. For a custom implementation, use **Qiskit SDK as the primary circuit representation and elementary state-evolution toolkit**, with an independent visualization and tracing layer. Treat **Qiskit Aer as an optional backend** rather than a critical architectural dependency: its maintainers explicitly report *reduced maintenance mode*. Preserve a simulator adapter boundary for a future **Cirq** backend.

**Do not** write a new high-performance universal statevector or density-matrix engine unless the project itself becomes an exercise in numerical simulation. The added value should be educational inspection, pedagogy, and reproducible workflows.

## 1. Product brief

### 1.1 Problem

Students can construct and execute quantum algorithms but often find it difficult to relate gate diagrams to evolving amplitudes and phases, entanglement, reduced states, actual measurement collapse, conditional operations, and algorithm behavior. Existing toolkits offer many components, but the visual and mathematical views are scattered or, in some browser editors, measurement behavior is idealized or omitted from live inspection.

### 1.2 Intended users

1. First-time quantum information students using example circuits and graphical inspection.
2. Students implementing graded and exploratory algorithms in Python.
3. Advanced users teaching, prototyping, or comparing simulation approaches.

### 1.3 User workflows

- **Guided demo:** Choose a Bell-state lesson → see annotated circuit → advance gate by gate → examine state and reduced states → choose or sample a measurement outcome → view branch state → repeat shots.
- **Code-first:** Import or write a Python `QuantumCircuit` locally → inspect a generated execution trace and visualizations → save/export results.
- **Circuit composition:** Create a parameterized subcircuit → save as a named reusable block → expand/collapse the block in the visualizer.
- **Experimentation:** Change parameter or initial state → compare exact probabilities, samples, or noise settings → export reproducible experiment data.

### 1.4 Non-goals for first release

Large-scale quantum advantage benchmarking; real-hardware job scheduling; untrusted multiuser Python execution; pulse-level control; full OpenQASM 3 semantics; general photonic and continuous-variable simulation; fault-tolerant error-correction benchmarking; hardware-calibrated noise models.

## 2. Formal requirements

Priority labels: **P0** first usable release; **P1** classroom-ready follow-on; **P2** optional extensions.

### 2.1 Circuit creation and composition

| ID | Requirement | Priority | Acceptance criterion |
|---|---|---|---|
| FR-01 | Python circuit construction | P0 | Ordinary Qiskit `QuantumCircuit` works with public tracing API. |
| FR-02 | Standard gates | P0 | X, Y, Z, H, S, T, Rx/y/z, CNOT, CZ, SWAP, Toffoli supported. |
| FR-03 | Arbitrary legal unitary matrices | P0 | Validate unitarity and correct target dimensions; simulate feasible custom gates. |
| FR-04 | Arbitrary initial states | P0 | Basis states, product states, normalized statevectors. |
| FR-05 | Parameters | P0 | Bind rotations and update the trace without editing the implementation. |
| FR-06 | Composite blocks | P0 | Name, parameterize, append, collapse, and expand subcircuits. |
| FR-07 | Circuit diagrams | P0 | Control/target wires, measurement wires, current-operation highlight. |
| FR-08 | Circuit editing in UI | P1 | Add/remove gates and synchronize graphical representation with canonical circuit. |
| FR-09 | Import/export | P1 | QPY and supported OpenQASM subsets with explicit diagnostics for unsupported constructs. |

### 2.2 Simulation and state inspection

| ID | Requirement | Priority | Acceptance criterion |
|---|---|---|---|
| FR-10 | Gate-by-gate evolution | P0 | Inspect state before and after each supported unitary operation. |
| FR-11 | Measurement branches | P0 | Enumerate possible measurement results and correct conditional post-measurement states for small circuits. |
| FR-12 | Measurement sampling | P0 | One-shot seeded sampling and repeated-shot seeded histograms agree statistically with Born probabilities. |
| FR-13 | Exact vs sampled results | P0 | Clearly label analytic probabilities separately from finite-shot observations. |
| FR-14 | Statevector visualization | P0 | Show complex amplitudes, phases, normalized magnitudes, and basis probabilities. |
| FR-15 | Bloch/reduced states | P1 | A Bell pair produces a reduced Bloch vector at the origin for either single qubit. |
| FR-16 | Density matrices | P1 | Display partial traces, purity, and correctly represent mixtures. |
| FR-17 | Feedforward and reset | P1 | Mid-circuit measurement followed by conditional X/Z behaves correctly. |
| FR-18 | Noise channels | P1 | Support at least depolarizing, amplitude damping, phase damping, and readout-error examples. |
| FR-19 | Backend-agnostic simulation | P2 | Stable adapter API; independent Cirq backend can be added without UI changes. |
| FR-20 | Specialized simulators | P2 | Stabilizer/MPS or other methods selected when appropriate and capability-checked. |

### 2.3 Visuals, lessons, and sharing

| ID | Requirement | Priority | Acceptance criterion |
|---|---|---|---|
| FR-21 | Interactive step timeline | P0 | Move backward/forward; select steps; compare input/output states. |
| FR-22 | Educational gallery | P0 | Bell, GHZ, measurement bases, teleportation, superdense coding, Deutsch–Jozsa, Grover, QFT. |
| FR-23 | Explanations and predictions | P1 | Markdown/LaTeX notes; students can predict before revealing state or outcome. |
| FR-24 | Parameter sweeps | P1 | Plot state probability or fidelity vs gate parameter. |
| FR-25 | Export reproducibility | P1 | Save circuit, settings, RNG seed, backend/software versions, and selected result data. |
| FR-26 | Online sharing | P2 | Serialize safely supported circuits for share links; no arbitrary code execution. |
| FR-27 | CV support | P2 | Future separate adapter for Gaussian states/channels and phase-space visualizations. |

### 2.4 Nonfunctional requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-01 | Local installation | Mac (Intel/Apple Silicon), Windows, Linux; no account needed. |
| NFR-02 | Python environment | Start with Python 3.12; pin compatible package versions in `uv.lock`. |
| NFR-03 | Development | `uv`, `pytest`, Ruff, type checking, CI, `src/` packaging. |
| NFR-04 | Numerical validation | Unitary normalization, Born probabilities, Hermiticity/trace of density matrices, analytic test circuits. |
| NFR-05 | Limits | Estimate state memory before execution and warn/fail safely. |
| NFR-06 | Accessibility | Color-independent phase labels, keyboard navigation, readable equations, light/dark themes. |
| NFR-07 | Reproducibility | Seeded stochastic executions, deterministic traces for deterministic circuits, export manifest. |
| NFR-08 | Security | Bind local server to loopback by default; no arbitrary uploaded Python execution; validate file sizes and inputs. |
| NFR-09 | Extensibility | Model/simulator/view separation and backend capability negotiation. |
| NFR-10 | Documentation | README landing page; `docs/` requirements/architecture/tutorials/version changes; examples folder. |

### 2.5 Performance and representation guidance

For `n` qubits, a complex128 statevector uses approximately `16 × 2^n` bytes, and a dense complex128 density matrix uses `16 × 4^n` bytes before overhead. Examples: 10 qubits: statevector 16 KiB, density matrix 16 MiB; 20 qubits: 16 MiB versus 16 TiB. The interface should avoid rendering all `2^n` basis states beyond a small threshold. Use top-k, aggregation, sampling, or sparse displays, with clear notices about omitted detail.

**Practical initial target:** Pleasant interactive use for 1–8 qubit tutorial circuits. A larger supported circuit may run in the backend even if the UI limits exhaustive display. Include configurable memory, branch-count, and shot-count caps.

## 3. Physics and pedagogical correctness

1. **No measurement = unitary state evolution:** `|ψ'⟩ = U |ψ⟩`.
2. **Conditional projective measurement:** for projectors `P_m`, `p(m) = ⟨ψ|P_m|ψ⟩`, and conditional state `|ψ_m⟩ = P_m|ψ⟩ / sqrt(p(m))` when `p(m)>0`.
3. **Nonselective measurement:** `ρ' = Σ_m P_m ρ P_m` is generally mixed. This is *not* the same as selecting a single branch.
4. **Reduced state:** `ρ_A = Tr_B(ρ_AB)`; a pure Bell pair has locally mixed qubits.
5. **Local Bloch sphere:** show `r=(Tr(ρX), Tr(ρY), Tr(ρZ))` and interior vectors for mixed states rather than implying all states lie on the sphere surface.
6. **Bit ordering:** adopt/document Qiskit's little-endian computational basis labels; show wire index and basis-string index distinctly.
7. **Global phase:** should not be shown as a physically observable probability change. Display relative phases in context.
8. **Shot counts:** finite-shot experiments fluctuate and must be distinguished from exact analytic probabilities.
9. **Branch explosion:** for numerous mid-circuit measurements, branch enumeration grows exponentially. Cap exact branching and fall back to sampling or hide unsupported modes.
10. **Physical meaning:** inspecting the complete simulated state is a debugging/teaching convenience, not something a hardware execution directly reveals from one shot.

**Golden Bell-state fixture:** Starting with `|00⟩`, apply `H(0)` to obtain `( |00⟩ + |01⟩ )/sqrt(2)` using Qiskit's displayed `|q1 q0⟩` labels; `CX(0,1)` yields `( |00⟩ + |11⟩ )/sqrt(2)`. Measuring `q0` branches to `00` or `11` with probability `1/2` each. Before measurement the single-qubit reduced states both equal `I/2`.

## 4. Existing software review (as of 2026-10-22)

The evaluation focuses on (a) active/company/community stewardship, (b) programmable circuit composition, (c) intermediate state inspection, (d) measurement/noise fidelity, and (e) fit for a teaching interface. Capability assessments are *documentation-based*; they are not a completed interoperability or installation benchmark.

| Product | Stewardship | Strengths | Fit / limitation |
|---|---|---|---|
| **IBM Quantum Composer** | IBM (company) | Browser-based drag/drop, gate groups, OpenQASM editing, generated Python, circuit inspector, q-sphere and histograms | **Closest ready-made teaching UI.** Its live visualization explicitly ignores measurements; generated Qiskit text is read-only; unsigned users get visualizations for up to four qubits. |
| **Quirk** | Created/led by Craig Gidney (individual + contributors; not official Google product) | Instant browser-based circuit editing, inline amplitude/probability/Bloch/density displays, linkable circuits | Very low friction; lacks robust measurement recoupling and full Python framework; documentation mentions up to 16 qubits. |
| **Quirk-E** | University of Jyväskylä research group | Builds on Quirk, adds step inspector, OpenQASM 2 import, export subsets, gallery, plots, VS Code extension | Strong teaching prototype and possible short-term alternative; imports/exports are not universally faithful; inherits architectural concerns of Quirk, so test measurement semantics before depending on it. |
| **Qiskit SDK** | IBM-led with broad open-source community | Rich Python circuit definitions, custom gates, transpilation, statevector/density matrix information, circuit/state figures | Excellent primary circuit API; requires our own unified educational step UI. Recent release: 2.5.2 (Aug 2026). |
| **Qiskit Aer** | Qiskit/IBM-associated maintainer community | State/density/stabilizer/MPS simulation, save-state instructions, noise channels and shot sampling | High capability, but repo explicitly states **reduced maintenance: critical bugs prioritized; enhancements backlogged**. Keep optional behind adapter. |
| **Cirq** | Google Quantum AI + contributors | Python circuit composition; `simulate_moment_steps`; density-matrix simulator, noise, parametric circuits | Very strong alternative backend for tracing; ‘moment’ steps may contain parallel gates and differ from single-gate tracing. |
| **QuTiP + qutip-qip** | Independent open-source scientific community | Quantum objects, partial trace, open-system physics, circuit `CircuitSimulator.step`, measurement branch statistics | Strong pedagogical physics foundation; less immediately aligned with a typical Qiskit-based curriculum and web UI. |
| **PennyLane** | Xanadu + open-source contributors | Python quantum functions, snapshots, pure/mixed simulation, differentiation and hybrid algorithms | Good if extending into quantum machine learning; not primarily a pedagogical drag-and-drop app. |
| **Amazon Braket SDK** | AWS (company) + contributors | Python circuits, local and remote simulators, reusable gates, noise | Robust cloud-ready choice; for educational inspection, needs custom UI and tracing. Remote QPU/managed service usage may have cost and account requirements. |
| **Microsoft Quantum Development Kit** | Microsoft (company) | Q#, OpenQASM, circuit diagramming, testing/debugging, local development | Full framework, but introduces Q# and another teaching language; no ready-made equivalent of the proposed integrated student UI. |
| **qc-1** | Andre Paquette (independent individual project) | Browser/offline simulation, step views, lots of analyses, QASM/Qiskit export, noise support per repository | Worth experimenting with, but newer independent work requires extra validation of release/test/support maturity before instructional adoption. |

### Detailed caveats that affect the decision

- **Composer is closer than a Python package to our desired UI**, and includes inspection and custom groupings. However, the official docs say live visualizations ignore added measurement operations. Treat that gap as decisive if a main lesson involves measurement-conditioned correction.
- **Quirk-E is substantially more relevant than original Quirk** for this project: it includes a step inspector and file-format interoperability; its export support applies only to a subset of gate configurations, per its guide.
- **Qiskit SDK and Qiskit Aer must be assessed separately.** The core SDK remains actively released; Aer warns about limited staffing and changes. Avoid making a v0.1 design depend on speculative Aer enhancements.
- **Cirq vs QuTiP:** Cirq excels at programmatic moment-by-moment iteration, while QuTiP offers direct per-gate stepping and quantum-physics-oriented representations.
- **Cloud dependence:** Qiskit/Cirq/QuTiP/PennyLane and Braket's local simulator do not inherently require paying for remote quantum hardware. Hardware/cloud services are optional and may have separate restrictions or prices.

### Selection scoring

Use a hands-on trial rather than pretend numeric scores are objective. For the initial proof-of-concept, weight criteria: 30% state/measurement correctness; 25% ease of student adoption; 20% Python extensibility; 15% maintainability; 10% future delivery flexibility. If a product fails mid-circuit conditional measurement, that is a **blocking issue** for teleportation as a showcase lesson even if its aggregate score is high.

## 5. Adoption path (no new custom software)

1. Have students use **IBM Quantum Composer** to draw and inspect ideal/unitary circuits, including Bell/GHZ, Grover, and QFT examples. Demonstrate the custom-gate grouping tool and the generated OpenQASM/Python outputs. Point out that live visualizations ignore measurement gates.
2. Use **Quirk-E** as an additional, browser-based playground for quick circuit experiments and the step inspector, and attempt imports from a controlled OpenQASM 2 subset.
3. Supply a **version-pinned Qiskit notebook collection** for genuine per-measurement analysis. Use Qiskit SDK `Statevector`/`DensityMatrix` for analytic states and Aer only when needed for complex noisy trajectories/sampling.
4. In class, compare **exact outcome probabilities** with finite-shot histograms and discuss the physical distinction.
5. Reassess custom development after the friends test a fixed set of lessons. If tool switching and state/measurement confusion remain problematic, build the integrated interface.

## 6. Custom software architecture

### 6.1 Technology stack

- **Language/core:** Python 3.12+; `qiskit` for canonical `QuantumCircuit`, statevector and density-matrix operations; NumPy, SciPy; Pydantic for serialized lesson/result schemas.
- **Optional simulator plug-ins:** `qiskit-aer` for advanced noise, trajectories and efficient methods; Cirq through an adapter later; QuTiP for independent test/reference implementations when appropriate.
- **Client:** React + TypeScript with a structured circuit rendering layer; Plotly for interactive amplitude/phase/count/state matrices and Bloch visualizations; KaTeX/MathJax for formula text; Monaco editor optional after the core is stable.
- **Local service:** FastAPI + Uvicorn running on `127.0.0.1`; launch via CLI command, opening a local browser tab. No cloud or authentication needed locally. Separate build-time frontend assets from the Python API so it can be hosted later.
- **Tooling:** `uv`, `pytest`, Ruff, `mypy`/Pyright, Playwright for UI tests, GitHub Actions, `mkdocs` or equivalent for docs.

**Why a browser-based local UI instead of Qt first?** It is cross-platform and can be reused if the project is hosted online. The app would still work offline on the user's machine. Future packaged desktop launchers could wrap it, but v0.1 should not be delayed by installer packaging.

### 6.2 Conceptual flow

```text
Python / QPY / supported QASM / Lesson Definition
                      |
             Validation + Normalization
                      |
          Canonical Qiskit QuantumCircuit
                      |
             Trace / Execution Controller
             /                     \
    Ideal-state engine        Adapter capability layer
  (state, projections,         Aer / future Cirq backend
   branching, sampling)              |
             \                     /
               Trace Result Model
             (steps, states, paths,
              probabilities, samples)
                      |
                  API Layer
                      |
     Circuit | State | Measurement | Lesson
                Interactive Views
```

The `Trace Result Model` should be our own, simple typed data contract; **do not** reimplement the core Qiskit circuit representation. Fields should include `step_index`, `operation`, `qubits`, `clbits`, `branch_id`, `branch_probability`, `seed`, `state_format`, `state_payload` (bounded by resource policy), and `backend_capabilities`.

### 6.3 Interfaces and separation

- `CircuitSource`: Qiskit circuit or validated imported format.
- `TraceEngine`: yields state/branch checkpoints with stable semantics and explicit support constraints.
- `SimulatorAdapter`: ability to run seeded shots, noise modes, or alternate representations; reports capability descriptors.
- `VisualizationModel`: derives amplitudes, relative phases, probabilities, partial traces, reduced Bloch vectors, purity.
- `Lesson`: markdown content, circuit factory, parameter fields, expected invariants, exercises.
- `ProjectBundle`: saved circuit, lesson/parameters, environment and backend versions, random seed, and reproducible result summary.

### 6.4 Measurement implementation design

**A. Ideal deterministic tracing:** gate operation evolves statevector. Maintain the convention and checkpoint after every operation (including composite operations when expanded).

**B. Conditional branch explorer:** upon projective measurement, compute probabilities of each outcome; copy the normalized conditional state for each nonzero-probability branch; track classical register values independently on each branch. UI can select a branch or display a branch tree. Cap the number of exact branches.

**C. One-shot execution:** sample one measurement trajectory with a fixed seed and record classical values.

**D. Nonselective density-matrix display:** sum the postmeasurement branch densities weighted by branch probabilities; label this as outcome-forgotten ensemble, not a single observed outcome.

**E. Feedforward:** after measurement, classical predicates govern which gates execute on each branch. Unsupported dynamic control-flow operations should fail explicitly rather than silently produce a misleading trace.

**F. Noisy extensions:** use appropriate density-matrix or trajectory implementation from an established backend; report when ideal-only visualization is displayed alongside noisy shot results.

## 7. Repository proposal

```text
quantum-circuit-explorer/
├── README.md
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .github/workflows/
├── docs/
│   ├── requirements.md
│   ├── ecosystem-review.md
│   ├── architecture.md
│   ├── conventions.md
│   ├── development.md
│   ├── changelog.md
│   └── releases/
├── src/quantum_circuit_explorer/
│   ├── circuits/
│   ├── simulation/
│   ├── traces/
│   ├── visualization/
│   ├── lessons/
│   ├── api/
│   └── cli.py
├── frontend/
│   ├── src/
│   └── package.json
├── examples/
│   ├── bell_state.py
│   ├── teleportation.py
│   ├── grover.py
│   └── qft.py
└── tests/
    ├── unit/
    ├── integration/
    ├── numerical/
    └── e2e/
```

`README.md` is the concise homepage: what it does, animated screenshot, quick install/start, example, feature matrix, contributing/docs links. Move detailed math, APIs, backend limitations, and developer instructions into `docs/`. A GitHub Wiki can later mirror stable tutorials and examples, but the canonical technical documentation should stay versioned in the repository to avoid drift.

## 8. Proposed phased development

### Phase 0 — Existing-software evaluation

- Pilot the same three circuits in Composer, Quirk-E, and Qiskit: Bell measurement, teleportation with classical feedforward, Grover's amplitude amplification.
- Check support for repeated measurements, mid-circuit resets, exact branch states, and supported imports.
- Document each discrepancy and decide if notebook + browser tool already meets the friends' actual needs.
- Record test environments and versions.

**Exit condition:** either choose the no-build adoption path or establish at least two material gaps requiring a custom app.

### Phase 1 — v0.1: Scientific core and trace library

- Set up repository, CI, docs, Qiskit SDK, type-checked trace result schema, initial analytic state and branch explorer.
- Build Python API `trace(circuit, initial_state=..., options=...)` and CLI examples.
- Visualization outputs: circuit diagrams, amplitude table, probabilities, phase plot, simple measurement path and counts.
- Include Bell, GHZ, measurement bases, and teleportation fixtures.

**Exit condition:** exact test circuits, measurements and seeded runs agree with analytic expected results and independent Qiskit simulations.

### Phase 2 — v0.2: Local interactive educational UI

- Launch local web UI; circuit viewer; timeline; stepping; branch selection; amplitude/phase/probability displays; lessons.
- Implement composite-gate expansion and user-chosen initial states.
- Cache traces and cap high-cost requests.

**Exit condition:** a novice can run and understand the Bell-state and teleportation lessons without needing separate tools.

### Phase 3 — v0.3: Full classroom functionality

- Mixed-state tools, reduced Bloch vectors, partial traces, purity, noise, comparison of analytic vs sampled results, parameter sweeps.
- QPY/OpenQASM import, project save/load, reproducibility manifest, export SVG/PNG/CSV/JSON as appropriate.
- Optional Aer adapter, tested under pinned compatible versions; warnings for unsupported features.

**Exit condition:** regression tests cover noisy states, classical feedforward, entanglement, and selected imports.

### Phase 4 — v0.4+: Distribution and enhancements

- Graphical circuit editor and palette; improved lesson authoring; optional local installer.
- Backend adapter proof-of-concept with Cirq.
- Evaluate online hosting with a constrained circuit representation and strict resource limits rather than executing arbitrary uploaded Python.
- Optional dedicated CV/photonic simulation plug-in only if there is demonstrated demand.

## 9. Acceptance and regression cases

1. **Hadamard:** `H|0⟩ = (|0⟩+|1⟩)/sqrt(2)`; two outcomes exactly 1/2.
2. **Z-phase interference:** `H Z H |0⟩ = |1⟩` up to irrelevant global phase.
3. **Bell pair:** `H(q0)`, `CX(q0,q1)`; output `(|00⟩+|11⟩)/sqrt(2)`; reduced single-qubit state `I/2`.
4. **Bell measurement branching:** measure q0; branch states `|00⟩` and `|11⟩` each probability 1/2.
5. **Teleportation:** arbitrary input `α|0⟩+β|1⟩`; after two-bit measurement and conditional correction, receiver's reduced output agrees with input up to numerical tolerance.
6. **Density-matrix validity:** `Tr(ρ)=1`, `ρ=ρ†`, eigenvalues nonnegative within tolerance; pure-state consistency.
7. **Readout/noise:** increasing depolarizing noise trends as expected for selected simple fixtures; never assume every observable is monotonic.
8. **Parameter binding:** `Rx(0)` returns original, `Rx(π)` maps `|0⟩` to `|1⟩` up to phase.
9. **Bit-order test:** applying `X(q0)` to `|00⟩` is displayed as `|01⟩` with Qiskit label convention.
10. **Resource guard:** 20-qubit density-matrix request is refused or safely rerouted based on memory policy.
11. **Random sampling:** tests use fixed seeds for reproducibility; statistical assertions use appropriate tolerances, not exact 50/50 counts.
12. **Unsupported control flow:** raises an understandable error; never silently drops measurement or classically controlled gates.

## 10. Decision rubric and immediate next step

**Choose existing tools** if students mainly want to drag gates, inspect unmeasured unitary circuits, and work with common textbook examples. Composer and Quirk-E already do much of this.

**Build the proposed app** if integrated code-first workflows, measurement/collapse fidelity, branching, and lesson-specific explanations are essential. This is the likely better long-term project, provided you want to maintain it.

**First practical step:** complete a three-tool, three-circuit acceptance pilot and log where the visualization becomes pedagogically misleading or awkward. Then use those tests as v0.1 product specifications rather than creating a generic quantum IDE from scratch.

## 11. Primary sources and relevant links

Official vendor/project documentation, accessed for this October 2026 review:

- IBM Quantum Composer guide: https://quantum.cloud.ibm.com/docs/en/guides/composer
- Qiskit SDK: https://quantum.cloud.ibm.com/docs/api/qiskit
- Qiskit SDK releases: https://github.com/Qiskit/qiskit/releases
- Qiskit bit order: https://quantum.cloud.ibm.com/docs/en/guides/bit-ordering
- Qiskit Aer: https://github.com/Qiskit/qiskit-aer
- Aer simulator API: https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html
- Aer snapshot instructions: https://qiskit.github.io/qiskit-aer/apidocs/aer_library.html
- Cirq simulation: https://quantumai.google/cirq/simulate/simulation
- Cirq project: https://github.com/quantumlib/cirq
- QuTiP: https://qutip.org/
- QuTiP qip simulator: https://qutip-qip.readthedocs.io/en/stable/qip-simulator.html
- PennyLane circuit inspection: https://docs.pennylane.ai/en/stable/introduction/inspecting_circuits.html
- AWS Braket circuit construction: https://docs.aws.amazon.com/braket/latest/developerguide/braket-constructing-circuit.html
- Microsoft QDK: https://learn.microsoft.com/en-us/azure/quantum/qdk-main-overview
- Original Quirk: https://github.com/Strilanc/Quirk
- Quirk-E guide: https://quirk-e.dev/guide/
- Quirk-E repository: https://github.com/DEQSE-Project/Quirk-E
- Independent `qc-1` project: https://github.com/thepacket/qc-1

**Qualification:** Maintainer identity and features are supported by project documentation. This review has not benchmarked local installation, cross-platform wheels, and every import/export edge case. These belong in Phase 0 hands-on acceptance testing.
