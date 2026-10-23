# Quantum Computing & Communication Workbench — Design Requirements and Roadmap

**Design revision:** v0.2  
**Date:** 2026-10-22  
**Status:** Planning; supersedes the scope and roadmap in `quantum_circuit_explorer_design_review_v0.1.md`  
**Primary audience:** Students studying quantum information science, instructors, and exploratory researchers  
**Primary use:** A local-first, Python-programmable educational quantum workbench with modern visualizations and reusable algorithm/protocol components.

## 0. What changed since v0.1

The original requirements were revised after direct use of IBM Quantum Composer and Quirk-E:

- **Composer:** Good for basic gates, but cumbersome for extensive algorithms such as QPE and Shor's algorithm.
- **Quirk-E:** Strong precedent for visual inspection, but the observed UI does not show the desired histogram for 7+ wires; its visual design could be modernized. The seven-wire observation is a user-observed behavior, **not yet an independently verified hard simulator limit**.
- **New focus:** scalable **collapsible circuits**, **adaptive probability visualization**, algorithm-oriented inspection, and a **dedicated communication protocol layer**.
- **New scope:** BB84 and subsequent communication protocols, including an explicit classical channel, attacks, noise, sifting, reconciliation, privacy amplification, and—in separate workflows—quantum error correction.
- **Decision:** Build a new frontend, execution tracing service, algorithm composition utilities, and protocol engine around established numerical simulators. Do not initially fork Quirk-E or write a statevector engine from scratch.

## 1. Mission, scope, and non-goals

> Allow a student to write or visually assemble a quantum circuit or communication protocol, execute it one step at a time, inspect the mathematical and physical state, and understand how algorithmic structure, measurement, randomness, and classical communication determine the result.

**Core modes:** (A) Circuit Lab, (B) Algorithm Lab, (C) Communication Lab, (D) Error-Correction Lab. All reuse shared circuit definitions, execution records, visualizations, and lessons.

**P0 goals:** Python-programmable qubit circuits; validated gate/subcircuit composition; measurement and reset semantics; state snapshots; efficient rendering of many-wire circuits and selected-register distributions; QFT and QPE examples; ability to run without an external service.

**P1 goals:** richer UI editing; a toy Shor order-finding/factoring demonstration with honest limitations; BB84 with Alice/Bob/Eve and classical postprocessing; reduced density matrices/noise; more export formats.

**P2 goals:** E91/BBM92, B92, teleportation over channels, entanglement swapping; small quantum error-correcting codes and decoding; specialized stabilizer and network backends; hosted lessons.

**Non-goals initially:** factoring cryptographically meaningful numbers; universal simulation of arbitrarily many qubits; authenticated QKD deployment; claims of provable finite-key security without a corresponding proof/model; quantum hardware integration; a full fiber-optics or discrete-event network simulator; CV/photonic gate support in the initial engine.

## 2. Prioritized functional requirements

| ID | Requirement | Priority | Initial acceptance criterion |
|---|---|---|---|
| CIR-01 | Python API for arbitrary valid supported circuits | P0 | Qiskit `QuantumCircuit` accepted or translated with explicit errors. |
| CIR-02 | Named and parameterized composite gates | P0 | Save QFT, controlled-U, arithmetic block; expand/collapse in UI. |
| CIR-03 | Configurable registers and subcircuits | P0 | Separate phase, work, ancilla, and classical registers with labeled wires. |
| CIR-04 | Custom gates and controlled versions | P0 | Construct controlled powers, validate unitaries and sizes. |
| CIR-05 | Programmable measurement/reset/feedforward | P0/P1 | Basic measurement P0; general classical control P1 with correct semantics. |
| SIM-01 | Exact feasible statevector evolution | P0 | Numerical equivalence to Qiskit on reference circuits. |
| SIM-02 | Trace checkpoints by gate, layer, or block | P0 | Navigate snapshots with register and gate metadata. |
| SIM-03 | Measurement branch tracing and repeated-shot sampling | P0 | Distinguish exact probabilities from empirical counts; allow conditional states. |
| SIM-04 | Resource estimates and backend selection | P0 | Prevent excessive-memory dense statevectors/density matrices. |
| SIM-05 | Density matrices, partial trace, standard quantum channels | P1 | Validate trace and positivity within numerical tolerance. |
| VIS-01 | Modern responsive circuit viewer | P0 | 20+ wire *rendering* without requiring full basis histogram. |
| VIS-02 | Adaptive distributions and histograms | P0 | Choose register, sort/top-k, search basis state; sampled/exact modes. |
| VIS-03 | Step, pause, select, collapse/expand block | P0 | Inspection works for QFT/QPE without displaying every inner gate. |
| VIS-04 | Bloch, amplitude/phase, reduced-density views | P1 | Physically appropriate views chosen based on state representation. |
| VIS-05 | Circuit-editor palette and drag-drop | P1 | Editing round trips through canonical circuit representation. |
| ALG-01 | QFT/inverse QFT and phase kickback lessons | P0 | Tests for known Fourier transforms and controlled-phase circuits. |
| ALG-02 | QPE with precision register readout | P0 | Exact representable phase; finite precision example; compare predictions. |
| ALG-03 | Shor order finding and classical postprocessing | P1 | Correct toy N=15 example; identify curated/compiled vs generic circuits. |
| ALG-04 | Arithmetic/oracle subcircuit library | P1 | Reusable controlled-U powers, adders, comparators as appropriate. |
| COM-01 | Quantum/classical channels and participant timeline | P1 | Alice/Bob/Eve with separately labeled classical and quantum messages. |
| COM-02 | BB84 educational simulator | P1 | Prepare/send/measure/sift/estimate QBER/reconcile/amplify trace. |
| COM-03 | Eavesdropping and channel-noise experiments | P1 | Switch between ideal, intercept-resend, and configurable noise. |
| COM-04 | Additional QKD and network protocols | P2 | E91/BBM92, B92, repeater/swapping demonstrations. |
| QEC-01 | Quantum codes and syndrome extraction | P2 | 3-qubit repetition codes; correctable X/Z faults. |
| QEC-02 | Specialized stabilizer backend and decoder | P2 | Optional Stim/PyMatching adapter and reproducible demonstrations. |
| IO-01 | Save/load examples and experimental settings | P0 | Versioned circuit/trace exports; seed, register ordering, backend tracked. |
| IO-02 | OpenQASM/QPY interoperability | P1 | Explicitly document exact supported subsets and round-trip limitations. |

P0/P1 refer to rollout phases, not a guarantee of immediate library coverage.

## 3. Visualization requirements for complex circuits

### 3.1 Hierarchical circuit viewer

Render both an overview and a drill-down for each composed block:

- Default overview may show `Prepare eigenstate -> H on phase register -> Controlled-U^{2^j} -> inverse QFT -> Measure`.
- Expand `Controlled-U^{2^j}` to show its decomposition without breaking the logical organization of the algorithm.
- Associate each logical block with an explanation, mathematical operation, source-code location, and state trace.
- Freeze register labels; zoom/pan horizontally and vertically; group/wrap visual layers as useful.
- The canonical circuit is the source of truth. A UI grouping is distinct from a native compiled gate.

### 3.2 Adaptive probability and measurement views

A full distribution over n bits has up to 2^n outcomes. **Do not show every outcome by default.** Provide:

1. **Register selection:** visualize only the measurement/phase/work register that matters.
2. **Top-k most likely outcomes:** default sorted probability or sampled count plot, plus remaining-mass accounting.
3. **Search/filter:** individual bitstrings, masks, Hamming weight, or marginal subsets.
4. **Sparse/nonzero mode:** represent only supported or measured outcomes, with explicit distinction from exact zero probabilities.
5. **Scalable data views:** table, virtualized bars, and downloadable CSV instead of unusable 2^n-wide charts.
6. **Correct uncertainty:** distinguish exact Born-rule probability from a finite-shot histogram and optionally show binomial uncertainty.
7. **Backend-aware UI:** statevector amplitudes are unavailable if only a stabilizer sampler or physical network model is running.

For a 7-wire circuit, show the complete 128-state distribution on demand; for larger circuits, the above views must remain usable and must never silently truncate the normalization.

### 3.3 Correct state and measurement semantics

- Permit premeasurement exact distributions separately from random **sampled** outcomes.
- Branch on projective measurement and record conditional post-measurement states.
- Maintain classical registers and subsequent conditional corrections.
- Preserve endian conventions and indicate ordering prominently.
- Use reduced density matrices for individual qubits in an entangled state rather than inventing pure single-qubit Bloch vectors.
- Handle errors/unsupported operations explicitly.

## 4. Algorithm Lab designs

### 4.1 Quantum phase estimation (priority showcase)

Expose the phase register (t precision bits), target eigenstate, controlled powers of U, inverse QFT, readout, and expected eigenphase. Include parameters `t`, U, initial eigenstate, and measurement shots. Enable two views:

- **Algorithm level:** blocks and mathematical phases, register state and phase histogram.
- **Gate level:** decompose any supported block, trace circuit operations, inspect interference.

Reference cases: for U with eigenvalue e^(2πiθ), demonstrate θ exactly expressible with t bits and θ requiring approximation. Distinguish a known eigenstate from arbitrary superpositions of eigenvectors; the latter produce a mixture of eigenphase outcomes.

### 4.2 Shor's algorithm (a sequence, not simply a picture)

Workflow: choose N and a coprime base a; classical gcd precheck; controlled modular multiplication / order finding; QPE; measure phase; continued-fraction candidate extraction; verify period r; attempt gcd(a^(r/2) +/- 1, N); repeat or report failure where appropriate.

For N=15, use clearly labeled small demonstrations. Separate **curated demonstrations / compiled or hardcoded modular multiplication** from **generic arithmetic oracles**. A circuit built from a dense N-qubit `UnitaryGate` does not establish efficient asymptotic Shor implementation; gate synthesis can be exponentially expensive. Larger instances depend on arithmetic construction and qubit resources.

Expose algorithm failures, not only successfully selected measurement outcomes.

## 5. Communication Lab

### 5.1 Domain model

Use `Participant` (Alice, Bob, Eve), `QuantumChannel`, `ClassicalChannel`, `Protocol`, `Message`, `Event`, `AttackModel`, `NoiseModel`, `Result`. Quantum/classical channel events are separate from conventional gates. Events have identifiers, logical timestamps, ownership, sent/received state metadata, and optional channel effects.

Each protocol produces a chronological **protocol event trace** in addition to per-circuit quantum state traces. Later, more realistic fiber/network delay should be optional and use a proper discrete-event backend.

### 5.2 BB84 minimum educational workflow

1. Alice randomly selects bits and encoding bases.
2. Alice prepares corresponding states and transmits them.
3. Bob selects measurement bases and records results.
4. Alice and Bob announce bases on an authenticated classical channel and sift their bits.
5. They sample or otherwise estimate QBER and determine whether to abort under the chosen *demonstration policy*.
6. If continuing, apply a transparent reconciliation example and account for leaked classical information.
7. Demonstrate privacy amplification, explaining that final secure key length depends on explicit security assumptions and estimates.
8. Show Eve's actions for an optional intercept-resend attack, and distinguish attacker effects from background noise.

The simulator must NOT declare a key "secure" simply because two bit arrays match. QKD requires authenticated classical communication and a model-appropriate security analysis. The teaching demo must label toy approximations and should avoid implying production cryptographic suitability.

UI: participant swimlanes; quantum vs classical message arrows; step timeline; Alice/Bob/Eve basis tables; sifted-key view; observed QBER; leak accounting; privacy-amplification output and abort reason.

### 5.3 Communication roadmap

- **First:** BB84 with ideal qubits, probabilistic Eve, and configurable simple noise.
- **Next:** B92 and E91/BBM92 with CHSH/correlation analysis as appropriate.
- **Next:** teleportation, superdense coding, entanglement swapping, repeater chains, entanglement distribution.
- **Later:** physical photon loss, dark counts, source defects, detector efficiency, realistic finite-key calculations, network topology and latency.

## 6. Classical and quantum error correction are separate layers

**QKD information reconciliation** handles differing *classical bit strings after measurement*. It may use a parity-exchange toy method initially; later use a well-specified classical reconciliation code and count information revealed over the authenticated channel.

**Quantum error correction (QEC)** protects an unmeasured encoded quantum state via syndrome extraction and correction; eventually include 3-qubit bit-flip and phase-flip codes, Steane's [[7,1,3]] code, and simple surface-code demonstrations.

A common educational visualization vocabulary can connect them, but they require different abstractions and should NOT be conflated.

Optional future libraries: **Stim** for Clifford/stabilizer circuits and detector models; **PyMatching** for suitable graph-based decoders. Stim cannot directly simulate non-Clifford components such as general T or Toffoli gates; the UI must explain backend restrictions.

## 7. Existing tools revisited

| Software | Governance | What it offers our plans | Recommended role |
|---|---|---|---|
| IBM Quantum Composer | IBM | Excellent immediate basics, but not ideal for complex algorithm navigation | Reference UX, not implementation foundation |
| Quirk-E | University of Jyväskylä research team; Apache-2.0 repo | Modernization inspiration; step inspector, histogram, imports/exports | Benchmark; consider fork only after technical audit |
| Qiskit SDK | IBM/community | Canonical Python circuits, gate and algorithm composition, ideal state evolution | **Primary initial circuit API** |
| Qiskit Aer | Qiskit ecosystem; reduced-maintenance notice | Noise and advanced simulation modes | Optional backend adapter |
| SeQUeNCe | Argonne-associated open-source project/research community | BB84, photonic components, resource and network models, event scheduler | Later physically richer network backend |
| QuNetSim | Research/community-maintained | Quantum networking abstractions and examples, including BB84/B92 | Protocol design reference; validate support status before adopting |
| NetSquid | QuTech, access subject to registration/terms | Sophisticated time-aware quantum network simulation | Specialized comparator, not default dependency |
| Stim | Quantumlib/Craig Gidney and contributors | Efficient large stabilizer simulations | Optional QEC backend |
| PyMatching | Research/community contributors | Fast minimum-weight perfect matching | Optional decoder |

**Quirk-E fork consideration:** Repository currently identifies Apache-2.0 licensing, which is compatible with many reuse scenarios subject to compliance. Its code and dependencies must still undergo architecture, compatibility, security, and maintainability review. A visual refresh alone does not resolve communication protocols, data model, multi-backend support, or complex programmatic algorithm workflows. Forking is an option, not the leading recommendation.

**Existing QKD offerings:** IBM publishes a Qiskit classroom lesson for QKD; QuNetSim supplies BB84/B92 examples; SeQUeNCe has a dedicated BB84 implementation. The distinctive gap is the *integrated, visually inspectable student workbench*, not the absence of any quantum communication software.

## 8. Architecture

```text
                          LOCAL WEB FRONTEND
   +-----------------+----------------+----------------+------------------+
   | Circuit Lab     | Algorithm Lab  | Communication  | Error-Correction |
   | editor, traces  | QFT/QPE/Shor   | timelines/QKD  | syndrome/decoder |
   +-----------------+----------------+----------------+------------------+
                                |
                           Application API
                                |
   +--------------------- Shared domain/services -------------------------+
   | circuit definitions | reusable blocks | registers | lesson metadata |
   | simulation trace    | protocol event log | experiment metadata       |
   +---------------------------+----------------------------------------+
                  |            |                    |
           Circuit adapter  Protocol engine       Analysis
                  |            |                    |
           Qiskit baseline  BB84/QKD initially   state plots,
           Aer optional     SeQUeNCe optional    histograms,
           Stim optional    more protocols       QBER/QEC
```

**Backend contracts:** `run_circuit`, `trace_circuit`, `sample`, `get_capabilities`, plus optional `run_protocol` and `run_qec_experiment`. Declare supported gates, measurement/control features, state representations, and size limits. Never silently approximate away measurements or unsupported behavior.

**Tech stack:** Python 3.12+ (verify compatible versions of each optional backend), Qiskit SDK, NumPy, FastAPI/Pydantic, pytest/Ruff, `uv`. Frontend React + TypeScript (or comparable lightweight modern stack) with virtualized circuit/distribution components. Use local service on loopback; browser access does not require user login. External deployment must use a sandboxed, constrained data/API format—never execute arbitrary contributed Python on the server.

**Project layout (sketch):**

```text
quantum-workbench/
  README.md                  # overview, uv setup, quickstart, supported features
  pyproject.toml / uv.lock
  docs/
    design-v0.2.md
    architecture.md
    conventions.md
    protocol-models.md
    versions/
  src/quantum_workbench/
    circuits/                 # blocks, registers, imports
    backends/                 # qiskit, optional aer/stim/sequence adapters
    execution/                # state trace, measurement branches
    algorithms/               # qft, qpe, shor, arithmetic components
    protocols/                # participants, channels, BB84 etc.
    qec/                      # toy codes and later decoders
    experiments/              # runner, reproducibility, plots
    api/
  frontend/
  examples/
    circuits/ algorithms/ communications/ qec/
  tests/
    unit/ integration/ reference/ ui/
  scripts/
    seed_demos.py
```

Prefer a versioned JSON data model for browser examples and traces. Add Python/Jupyter integrations without making notebooks the sole interface.

## 9. Roadmap and acceptance tests

| Release | Deliverable | Core acceptance |
|---|---|---|
| **Phase 0** | Decide reuse vs fork, explore exact seven-wire histogram observation | Run QPE/QFT and BB84 workflows in existing tools; inspect Quirk-E internals and licenses |
| **v0.1** | Python circuit API and trace model; dynamic register-selectable histogram | Exact phase and Bell/teleportation sanity cases; render 7+ wires/128 outcomes correctly |
| **v0.2** | Modern local circuit viewer; hierarchical QFT/QPE lesson | Parameterized QPE, expandable controlled-U and inverse-QFT; no full-state GUI freeze |
| **v0.3** | Shor toy demo + Communication Lab/BB84 | Correct classical postprocessing, failed measurement branches, sifting/QBER/Eve experiment |
| **v0.4** | Noise/reduced states + basic QEC examples | Density matrix validity; syndromes and correction on repetition codes |
| **v0.5+** | E91/B92, Stim/PyMatching, SeQUeNCe adapter and larger networks | Independent regression checks and explicit simulator limits |

**Specific reference cases:**

- Exact QPE phase θ=1/8 with t=3 returns the binary fraction `001` (up to the explicitly documented bit-order convention) with probability approximately one for the known eigenstate; document register conventions.
- QPE off-grid θ shows a spread and increasing precision improves approximation in aggregate, under a correct benchmark definition.
- Toy Shor factoring 15 recovers valid factors on qualifying outcomes, while unsuccessful branches are displayed and explained.
- A seven-qubit uniform superposition produces 128 nonzero computational-basis probabilities, each 1/128; the chart can show all 128 if requested.
- A large work register with a small phase register defaults to the phase-register marginal, not an entire-system histogram.
- Ideal BB84 with matching bases yields equal key bits (barring intentionally modeled errors); with basis mismatch, outcomes have correct randomness.
- Full intercept-resend under ideal, symmetric, randomly selected BB84 bases creates an **expected 25% QBER on sifted bits** in the asymptotic model; finite samples fluctuate.
- In the QKD workflow, a simulated classical bit-reconciliation step must not be reported as quantum syndrome decoding.
- A simple 3-qubit quantum bit-flip code corrects a single X error at an allowed position under the chosen perfect-syndrome model.
- Backend capability reporting prevents using Stim for general non-Clifford QPE/Shor circuits.

## 10. Engineering process

- Keep the README concise: purpose, screenshots or feature list, install with `uv`, launch instructions, basic example, links into `docs/`.
- Keep version-specific release/handoff documentation separate under `docs/versions/`; avoid rewriting the README into a change log.
- Run `uv sync --group dev`, `uv run pytest`, lint/type checks, reference numerical comparisons, manual UI acceptance before tagging a release.
- Use deterministic seeds for debugging; statistically proper tolerances for random experiments.
- Maintain a source/test matrix with known expected results and precise hardware/software convention definitions.
- Record mathematical assumptions for every communications and noise demo; do not present educational security demonstrations as production cryptography.

## 11. Source links (reviewed October 2026)

- IBM Quantum Composer: https://quantum.cloud.ibm.com/docs/en/guides/composer
- Qiskit QPE/factoring introduction: https://qiskit.qotlabs.org/learning/courses/fundamentals-of-quantum-algorithms/phase-estimation-and-factoring/introduction
- IBM Shor tutorial: https://quantum.cloud.ibm.com/docs/en/tutorials/shors-algorithm
- IBM QKD classroom module: https://quantum.cloud.ibm.com/learning/en/modules/computer-science/quantum-key-distribution
- Quirk-E: https://github.com/DEQSE-Project/Quirk-E and https://quirk-e.dev/guide/
- QuNetSim: https://github.com/tqsd/QuNetSim and https://tqsd.github.io/QuNetSim/examples/QKD_BB84.html
- SeQUeNCe: https://github.com/sequence-toolbox/SeQUeNCe and https://sequence-rtd-tutorial.readthedocs.io/stable/references/qkd/BB84.html
- NetSquid: https://netsquid.org/
- Stim: https://github.com/quantumlib/Stim
- PyMatching: https://pymatching.readthedocs.io/en/stable/
- QKD security context: https://journals.aps.org/rmp/abstract/10.1103/RevModPhys.81.1301
- Practical QKD postprocessing: https://www.mdpi.com/2227-7390/12/14/2243

**Confidence and limitations:** Documentation establishes the cited software features and project maintainers. No local benchmarking or interactive browser verification of Quirk-E's 7-wire histogram was performed for this revision. Engine choice, GUI behavior, and dependency compatibility should be confirmed in Phase 0.
