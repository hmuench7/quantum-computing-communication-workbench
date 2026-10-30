# v0.1 acceptance follow-up: Qiskit gates, dynamic control, and amplitude JSON

This supplement targets the three unchecked items in `docs/testing-v0.1.md`. It is an **additive acceptance patch**, not v0.2 and not a replacement for your existing repository. Existing local Ruff fixes (including exporting `uniform` in `__all__`) are preserved.

## Apply the patch

From your existing repository root, after downloading the archive:

```bash
unzip quantum_workbench_v0.1_acceptance_examples_patch.zip -d /tmp/qworkbench-acceptance
rsync -av /tmp/qworkbench-acceptance/quantum-computing-communication-workbench/ ./ \
  --exclude '.git' --exclude '.venv' --exclude 'uv.lock' --exclude 'outputs'
uv sync --extra dev --extra qiskit
uv run ruff check src tests examples
uv run pytest -q
```

The patch includes one change to `src/quantum_workbench/qiskit_adapter.py` to make dynamic `if_test` rejection informative; other changes only **add** examples/tests/documentation. No pre-existing `__init__.py` or README modifications are overwritten. Inspect `git diff` before committing.

If you already corrected the Ruff errors locally, keep those corrections. Ruff's error about `uniform` should be resolved by listing it in `__all__`, as you did.

## 1. Custom `UnitaryGate` and composed Qiskit gate

```bash
uv run python examples/acceptance_qiskit_gates.py
```

This example runs two cases on **both** NumPy and Qiskit simulation backends and also checks export back to Qiskit:

- **Custom X matrix + H + CX:** output should be `P(01)=P(10)=0.5`, all others 0. This is the Bell-like state `(\|01⟩+\|10⟩)/√2` in Qiskit little-endian order.
- **A Bell preparation built as `QuantumCircuit.to_gate()`**: output should be `P(00)=P(11)=0.5`, all others 0.
- The unitary-state vectors must agree with Qiskit's independent `Statevector.from_instruction()` reference within `1e-10`.
- The script should end with **`All Qiskit gate interoperability checks passed.`**

**Watch for:** an unsupported custom gate, incorrect qubit ordering, or a mismatch after conversion. A composed gate is currently imported as **one unitary operation**. It should work mathematically but will not expose the internal H/CX steps in the v0.1 trace. The future block-expansion interface will need to choose whether to preserve/decompose that information.

## 2. Dynamic `if_test` must be rejected explicitly

```bash
uv run python examples/acceptance_qiskit_control_flow.py
```

A **PASS** means `from_qiskit()` raises `UnsupportedOperationError`, and the script prints a message resembling:

```text
Qiskit classical control flow 'if_else' is unsupported in v0.1; conditional/loop bodies require dynamic simulation and cannot be silently omitted
```

The script checks that both `if_else` and `control flow` are in the error. **A successful import is a failure**, even if the circuit later runs: it would mean measurement-dependent correction was silently ignored. The full Qiskit circuit is printed before the expected rejection.

This verifies correct *boundary behavior*; implementing dynamic control is a future capability.

## 3. `--include-amplitudes` readability and size

```bash
uv run python examples/acceptance_amplitudes_json.py
```

The script runs the **actual CLI** four times (compact/expanded Bell; compact/expanded seven-qubit uniform), parses its `trace.json` outputs, and checks:

- JSON remains valid and legible, with `steps`, `branches`, and `amplitudes` fields.
- The expanded form records an array of `2^n` `[real, imaginary]` pairs for **each conditional branch**.
- Each conditional state is normalized (`Σ|αᵢ|² ≈ 1`) and branch probabilities for each step sum to 1.
- Compact and expanded exports preserve the same exact final probabilities and sampled counts.
- Expanded JSON is larger; the script prints both file sizes and their ratio (depends on machine/software formatting and chosen example).
- Bell state's nonzero amplitudes after H and CX should each be approximately `+0.70710678+0j`.

View the results at `outputs/acceptance-json/`. In particular, open the Bell expanded JSON in a code editor. The seven-wire case illustrates why **branch filtering, lazy loading, and compact state displays** will matter for a browser UI. Do not attach the entire seven-wire JSON to an issue report unless relevant; share the sizes and any surprising fields first.

## 4. Optional: radicals as *display* values

```bash
uv run --with sympy python examples/acceptance_symbolic_display.py
```

This standalone experiment demonstrates:

- `0.70710678` as `sqrt(2)/2`
- `0.86602540` as `sqrt(3)/2`
- `0.5` as `1/2`

The numerical statevector is unchanged. SymPy attempts to infer a compact expression from floating-point values; results can be coincidental or misleading for generic angles. **This must be labeled an approximate recognition, not an exact symbolic derivation.**

### Proposal for v0.2 symbolic state display

Use a display toggle `Numeric | Simplified`, and prioritize commonly occurring amplitudes and phases (small rationals, `√2/2`, `√3/2`, `i` multiples, simple roots of unity). Leave the simulation numeric. Only show a symbolic candidate when it is simple, numerically verified within tolerance, and accompanied by a way to view the original value. For genuinely exact algebra, we would need to carry symbolic gate expressions through the calculation, which is a larger and substantially slower feature.

## 5. Feedback to record before v0.2

- Which of the custom and composed Qiskit gate cases passed on the actual Mac installation? Did the imported composite gate's one-step trace feel limiting?
- Was the `if_test` error immediate and actionable? Copy the message if not.
- How large did `trace.json` get for the two expanded examples? Was its structure understandable?
- Did the optional radical display return intuitive expressions?

### Recorded UI direction

1. **Highest priority:** walk individual measurement branches, retaining both branch weights and conditional states.
2. Preserve inspect-a-gate and expand-a-block features, but defer making them the primary navigation mode.
3. A graphical editor is desirable eventually; static CLI plots are acceptable in the meantime.
4. Keep QPE distributions scoped to the measured precision register by default.
5. Add a symbolic-format *display option*; do not replace reliable numeric simulation with approximate symbolic guesses.

No increase in the package version is proposed for this test-only patch; the authoritative source remains `src/quantum_workbench/_version.py` at **0.1.0**.
