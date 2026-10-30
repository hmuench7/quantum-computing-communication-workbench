"""Optional proof-of-concept for symbolic display; it does not alter simulation.

Run from repository root (SymPy is a one-off extra, not a v0.1 dependency):
    uv run --with sympy python examples/acceptance_symbolic_display.py
SymPy recovers *plausible* formulas from floats; these are not exact proofs.
"""

from __future__ import annotations

import math

import sympy as sp

from quantum_workbench import Circuit, simulate

RADICALS = [sp.sqrt(2), sp.sqrt(3), sp.sqrt(5)]


def real_label(x: float, tolerance: float = 1e-10) -> str:
    if abs(x) <= tolerance:
        return "0"
    expression = sp.nsimplify(x, RADICALS, tolerance=tolerance, full=False)
    # Avoid presenting misleading or huge expressions inferred from floating point.
    if (len(str(expression)) > 35 or sp.count_ops(expression) > 8
            or abs(float(sp.N(expression)) - x) > tolerance):
        return f"{x:.8g}"
    return str(expression)


def show_state(title: str, circuit: Circuit) -> None:
    result = simulate(circuit)
    print(f"\n{title}")
    amplitudes = result.final.branches[0].amplitudes
    for index, value in enumerate(amplitudes):
        if abs(value) > 1e-10:
            real, imaginary = real_label(value.real), real_label(value.imag)
            expression = real if imaginary == "0" else f"({real}) + ({imaginary})*I"
            print(f"|{index:0{circuit.num_qubits}b}>: {value.real:+.8f}"
                  f"{value.imag:+.8f}j  ->  {expression}")


def main() -> None:
    show_state("H|0> = (|0>+|1>)/sqrt(2)", Circuit(1).h(0))
    show_state("Ry(pi/3)|0> = sqrt(3)/2|0> + 1/2|1>", Circuit(1).ry(math.pi / 3, 0))
    show_state("Bell state", Circuit(2).h(0).cx(0, 1))
    print("\nDisplay-only approximations; raw numeric amplitudes remain unchanged.")


if __name__ == "__main__":
    main()
