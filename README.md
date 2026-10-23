# Quantum Computing & Communication Workbench

[![Version](https://img.shields.io/badge/version-0.1.0-blue)](#version-and-release-notes)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](#requirements)
[![Status](https://img.shields.io/badge/status-educational%20prototype-lightgrey)](#scope-and-limitations)

**A local-first, Python-programmable workbench for inspecting quantum circuit evolution.**

The long-term project connects four related experiences: quantum **circuits**, **algorithms**, **communication protocols**, and **error correction**. Version **0.1.0** establishes the first part: a working, tested gate-model simulator with state checkpoints, exact measurement branching, reproducible shot sampling, and static circuit/distribution visualizations. It is a library and CLI, **not yet a browser-based interactive editor**.

## Highlights

- **Programmable qubit circuits:** one- and two-qubit gates, rotations, arbitrary finite-size unitary matrices, reusable unitary subcircuits, measurements, resets, barriers, and classical readout bits.
- **Inspect every operation:** exact weighted conditional states after projective measurements, without pretending a measured or reset entangled state is necessarily pure.
- **Seven-plus-wire histograms:** select a subset of qubits, show the top `k` outcomes, and account explicitly for omitted probability mass. The `uniform` seven-qubit demo includes all **128** possible outcomes.
- **Example algorithms:** Bell, GHZ, QFT / inverse QFT, finite-precision QPE with a known phase-gate eigenstate, measurement branching, and reset.
- **Reproducible results:** chosen simulation backend, random seed, exact probabilities, shot counts, and versioned JSON traces. Optional per-branch complex amplitudes can be exported.
- **Pluggable engines:** offline **NumPy reference statevector backend** (default) and optional **Qiskit Statevector** backend. An adapter accepts a supported subset of Qiskit `QuantumCircuit` programs.

## Requirements

- Python **3.11–3.14**. Python 3.12 or 3.13 is recommended.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended); alternatively standard Python packaging tools.
- macOS, Linux, or Windows. The CLI does not require a quantum cloud account.
- Enough memory for the selected dense state and trace. Defaults deliberately cap qubits, branches, and stored amplitudes.

## Installation

From a new, empty directory, extract the release ZIP and open the extracted project directory. On macOS/Linux:

```bash
# from the repository root
uv sync --extra dev --extra qiskit
uv run qworkbench --version
uv run qworkbench examples
uv run pytest -q
```

`uv sync` creates `.venv` locally. Qiskit is optional: if you want just the NumPy backend, use `uv sync --extra dev`. Both installations provide exactly the same circuit and trace API. The `--extra qiskit` flag enables import/export of supported Qiskit circuits and `backend="qiskit"`.

**Without uv** (for example, from a `venv` activated in the repository root):

```bash
python -m pip install -e '.[dev,qiskit]'
python -m pytest -q
qworkbench --version
```

**Dependency lockfile:** because the build environment had no access to the Python package index, a genuine `uv.lock` could not be resolved here. The first connected `uv sync` will generate it; commit that generated file for reproducibility. Do not treat the version ranges in `pyproject.toml` as an already-locked dependency set.

## Quick start

List included demonstrations:

```bash
uv run qworkbench examples
```

Run an exact QPE teaching example, save its circuit, histogram, sampled counts, and state trace:

```bash
uv run qworkbench run qpe --precision 3 --phase 0.125 \
  --shots 2048 --seed 42 --out-dir outputs/qpe
```

A phase of `0.125 = 1/8` is exactly representable with three precision qubits, so the expected phase-register measurement is **`001`**, with probability 1 up to floating-point error.

Run a seven-qubit histogram stress test:

```bash
uv run qworkbench run uniform --num-qubits 7 --top 16 \
  --out-dir outputs/uniform7
```

The chart shows 16 basis states and an **Other** bar totaling the remaining probability; use `--all` to draw all 128 states. Inspect a selected quantum register at a particular step:

```bash
uv run qworkbench run qpe --step 12 --qubits 0 1 2
uv run qworkbench run measurement --step 3 --branch 1
```

Compare the alternative backend:

```bash
uv run qworkbench run bell --backend qiskit --out-dir outputs/bell-qiskit
```

### Python API

```python
from quantum_workbench import Circuit, simulate
from quantum_workbench.visualize import plot_probabilities

circuit = Circuit(2, 2, name="Bell")
circuit.h(0).cx(0, 1).measure_all()

result = simulate(circuit, backend="numpy", shots=1000, seed=7)
print(result.summary())

# The state after H + CX, before measurement:
pre_measurement = result.steps[2]
print(pre_measurement.branches[0].amplitudes)

# Reduced exact distribution for just qubit 0:
print(pre_measurement.distribution(qubits=[0]))

plot_probabilities(result, top=16, path="outputs/bell-probabilities.png")
```

See [`examples/`](examples/) for demonstrations of custom circuits, trace inspection, and Qiskit interoperability.

### Qiskit interoperability

```python
from qiskit import QuantumCircuit
from quantum_workbench import simulate
from quantum_workbench.qiskit_adapter import from_qiskit

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

trace = simulate(from_qiskit(qc), backend="qiskit", shots=1024)
print(trace.summary())
```

This adapter supports unitary instructions that Qiskit can convert to an `Operator`, plus measurement, reset, and barriers. It **does not** accept dynamic classical control, nonunitary channels, delays, unbound parameters, or large standalone matrix gates. Unsupported instructions raise explicit errors rather than being ignored. The Qiskit backend is provided as a validation and interoperability route, not a speed promise.

## Outputs

With `--out-dir`, the CLI writes:

| File | Description |
|---|---|
| `trace.json` | Schema v1: simulation metadata, instructions, step-wise probabilities, branch weights/classical bits, final counts |
| `circuit.png` | Static gate timeline and measurement annotations |
| `probabilities.png` | Exact final classical readout by default, or selected-qubit quantum probabilities at an inspection step; with omitted-mass accounting |
| `counts.png` | Finite-shot histogram of *classical* measurement bits (or all qubits if the circuit has no classical bits) |

Use `--include-amplitudes` to store every conditional complex statevector in JSON, represented as `[real, imag]` values. This increases file size considerably. The JSON record describes a trace **but is not a lossless serialized circuit**; QPY/OpenQASM import/export and executable circuit round trips are later milestones.

## Testing

```bash
uv run pytest -q
uv run python -m compileall -q src tests examples
uv run ruff check src tests examples
uv run qworkbench run uniform --num-qubits 7 --out-dir outputs/uniform7
uv run qworkbench run qpe --precision 3 --phase 0.125 --out-dir outputs/qpe
```

See [`docs/testing-v0.1.md`](docs/testing-v0.1.md) for a manual acceptance checklist, failure reporting template, and numerical expectations. Do not commit the `outputs/` directory; it is intentionally ignored.

## Project structure

```text
quantum-computing-communication-workbench/
├── README.md                # entry point; install, usage, version
├── pyproject.toml           # package metadata and dependency ranges
├── src/quantum_workbench/
│   ├── circuits.py          # circuit representation, gates, subcircuits
│   ├── backends.py          # NumPy and optional Qiskit Statevector adapters
│   ├── execution.py         # deterministic gate trace, measurement branches, shots
│   ├── algorithms.py        # Bell, GHZ, QFT, QPE, demonstration circuits
│   ├── qiskit_adapter.py    # Qiskit circuit import/export
│   ├── visualize.py         # matplotlib circuit and distribution exports
│   ├── export.py            # versioned trace JSON
│   └── cli.py               # qworkbench command
├── examples/                # programmatic tutorial scripts
├── tests/                   # numerical, integration, CLI tests
├── docs/
│   ├── design/              # original v0.1 and revised v0.2 product requirements
│   ├── releases/            # individual release notes
│   ├── architecture.md      # design decisions and backend contract
│   ├── conventions.md       # bit ordering, measurements, reset, probabilities
│   └── testing-v0.1.md      # acceptance plan
└── LICENSE
```

## Scope and limitations

**v0.1 is intentionally a dense pure-state-trace prototype, not a universal hardware simulator.** The default guard is 12 qubits, 512 instructions, 256 conditional branches, and two million stored snapshot amplitudes. These guards can be adjusted via `Limits`, but resource costs still scale exponentially. The step tracer stores full conditional states, so it can be considerably more expensive than simply sampling a circuit.

*In scope:* unitary circuits, decomposed reusable blocks, projective Z-basis measurement, nonselective reset, exact premeasurement probabilities, conditional states, reproducible sample counts, and basic static figures.

*Not yet implemented:* browser UI, drag/drop circuit editing, true expandable diagrams, general classical feedforward, noise, density matrix inspection, BB84 or other communication protocols, error-correction decoders, full Shor modular arithmetic, high-performance many-qubit stabilizer/MPS simulation, and running arbitrary uploaded scripts securely. A QPE example for a **known eigenstate** is implemented; generic QPE oracle construction is not automated.

**Security note:** Quantum key distribution and protocol security have not been implemented or validated. This is educational software and should not be used for protecting real communications or managing security-critical keys.

## Version and release notes

Current release: **v0.1.0**. The single authoritative version source is `src/quantum_workbench/_version.py`; Hatchling reads it into package metadata and it is exposed as `quantum_workbench.__version__`. See [`docs/releases/v0.1.0.md`](docs/releases/v0.1.0.md) and the current [`product requirements`](docs/design/product-requirements-v0.2.md).

Future work focuses on a responsive hierarchical UI (v0.2), Shor / communications (later versions), and separate error-correction backends. Development plans are proposals, not claims of implemented features.

## Licensing and acknowledgements

MIT licensed (see [`LICENSE`](LICENSE)). Uses [NumPy](https://numpy.org/) and [Matplotlib](https://matplotlib.org/) and optionally [Qiskit](https://www.ibm.com/quantum/qiskit); their respective licenses remain applicable. IBM Quantum Composer and Quirk-E informed the educational UX requirements, but no code was copied from those projects.
