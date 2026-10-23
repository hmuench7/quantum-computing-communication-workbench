# v0.1 manual acceptance checklist

**Purpose:** evaluate correctness, practical usability, and whether the foundation is ready for a browser UI. Carry out in the checked-out/extracted repository root on your Mac.

## A. Install, environment, and quality gate

```bash
python3 --version
uv --version
uv sync --extra dev --extra qiskit
uv run qworkbench --version
uv run pytest -q
uv run ruff check src tests examples
```

Expected version: `0.1.0`. Every test should pass, including `tests/test_qiskit_optional.py` with Qiskit installed. If Qiskit tests fail, collect the complete traceback. The original package environment could not download Qiskit, so this is a **required** acceptance gate.

## B. Core physics checks

- [X] Bell state: `uv run qworkbench run bell --out-dir outputs/bell`. `P(00)=P(11)=0.5`; `01` and `10` are absent/zero. The distribution bar chart and counts plot are different things.
- [X] Inspect premeasurement entanglement: `uv run qworkbench run bell --step 2 --qubits 0`. Expect q0 probability 0.5/0.5, even though the **joint** state at step 2 is pure.
- [X] Conditional collapse: `uv run qworkbench run measurement --step 3 --branch 1`. Expect a branch with classical 1, probability 0.5, pure post-state `|11>`.
- [X] Branch zero: `uv run qworkbench run measurement --step 3 --branch 0`. Expect `|00>` and probability 0.5.
- [X] Reset: `uv run qworkbench run reset --out-dir outputs/reset`. Final quantum probability 0.5 for `00`, 0.5 for `10`, with two conditional branches. Reset q0 to 0 but do not claim the full entangled system remains pure.
- [X] Changing seed: rerun Bell with `--seed 1` and `--seed 2`. The exact probabilities should stay fixed, while sampled counts usually differ.

## C. Seven-wire and larger histogram

```bash
uv run qworkbench run uniform --num-qubits 7 --top 16 --out-dir outputs/uniform7
uv run qworkbench run uniform --num-qubits 7 --all --out-dir outputs/uniform7-all
uv run qworkbench run ghz --num-qubits 7 --out-dir outputs/ghz7
```

- [X] Seven-wire uniform case has **128 exact equally likely outcomes**, each `1/128 = 0.0078125`; 16 bars plus `Other` of `112/128 = 0.875` in the top-16 plot.
- [X] `--all` should render the complete 128-outcome histogram (crowded but not arbitrarily disabled).
- [X] Seven-wire GHZ only has two nonzero peaks, `0000000` and `1111111`.
- [X] For each run inspect `trace.json`, `circuit.png`, `probabilities.png`, `counts.png`.
- [X] Consider which filtering or presentation design would make the chart useful as the register grows; the current plots are only static proof-of-concept exports.

## D. Quantum phase estimation

```bash
uv run qworkbench run qpe --precision 3 --phase 0.125 --out-dir outputs/qpe-exact
uv run qworkbench run qpe --precision 3 --phase 0.3   --out-dir outputs/qpe-approx
uv run qworkbench run qpe --precision 4 --phase 0.625 --out-dir outputs/qpe-four
```

- [ ] Exact phase 1/8 in 3 precision bits: `001` probability ~1.
- [ ] Phase 0.3 in 3 precision bits: main outcomes `010` (~0.578) and `011` (~0.259), with other nonzero outcomes.
- [ ] Exact phase 0.625 in 4 precision bits: `1010` probability ~1.
- [ ] Inspect a stage with `--step` and select the precision register with `--qubits 0 1 2` or `0 1 2 3`.
- [ ] Examine `trace.json` step `block` labels for the inverse-QFT subcircuit. Decide what a **collapsible browser representation** should display in v0.2.

## E. Qiskit and custom code integration

```bash
uv run python examples/custom_circuit.py
uv run python examples/trace_walkthrough.py
uv run python examples/qiskit_interop.py
uv run qworkbench run qpe --backend qiskit --precision 3 --phase 0.125
```

- [ ] Qiskit-translated circuit probabilities agree with NumPy to numerical tolerance.
- [ ] Try a Qiskit circuit using a custom `UnitaryGate` or a composed gate; report unsupported cases.
- [ ] Try unsupported Qiskit dynamic `if_test` operations. The import should **fail clearly**, not silently omit classical control.
- [ ] Check `--include-amplitudes` JSON is readable but potentially large.

## F. Explicit guardrails

```bash
uv run qworkbench run ghz --num-qubits 12  # may exceed branch/snapshot guards; failure should be understandable
uv run qworkbench run ghz --num-qubits 13  # example rejects it explicitly
uv run qworkbench run uniform --num-qubits 7 --max-qubits 6  # resource guard
```

An expected error is not an automatic bug: identify whether it explains the limitation and next action. This is a **learning simulator**, not a benchmark of a 30-qubit dense engine.

## G. Questions before v0.2

1. Which interaction matters most: click-to-inspect a gate, walk individual measurement branches, or collapse an algorithm block?
2. Are static figures acceptable while you programmatically explore the examples, or would a GUI editor be required to make it useful for classmates?
3. Did the probability view show the right register by default, especially for QPE?
4. Which algorithms or gate types in your course could not be represented by the current API?
5. How intuitive were the distinction between branch probabilities, quantum-state marginals, and sampled classical counts?
6. Was installation reliable on your macOS architecture, including optional Qiskit?

## Issue report template

```text
System: macOS version / Intel or Apple Silicon / Python / uv / Qiskit versions
Command or script:
Expected:
Actual:
Error/traceback:
Output files/screenshots (optional):
Severity: blocks use / incorrect science / confusing UX / visual polish
Desired change:
```
