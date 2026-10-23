"""Static Matplotlib figures. A modern interactive browser UI is v0.2 work."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from quantum_workbench.circuits import Circuit
from quantum_workbench.execution import RunResult, top_k


def _save(fig, path: str | Path | None):
    if path is not None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(destination, dpi=160, bbox_inches="tight")
    return fig


def plot_probabilities(
    result: RunResult,
    *,
    step: int = -1,
    qubits: Sequence[int] | None = None,
    top: int | None = 16,
    sampled: bool = False,
    path: str | Path | None = None,
):
    """Plot top-k exact probabilities or final sampled outcome counts.

    ``qubits`` selects a quantum subsystem for exact probabilities; it is NOT
    a filter on the classical register. Counts refer to the measured classical
    register (if present), so counts+qubits is deliberately not supported.
    """
    if sampled and (qubits is not None or step not in (-1, len(result.steps) - 1)):
        raise ValueError(
            "Sampled counts are available only for final outcomes without qubit selection"
        )
    if sampled:
        distribution = {k: float(v) for k, v in result.counts.items()}
    elif qubits is None and step in (-1, len(result.steps) - 1) and result.circuit.num_clbits:
        # The default final histogram represents the actual classical readout,
        # not unmeasured work/ancilla qubits (especially important for QPE).
        distribution = result.outcome_probabilities
    else:
        distribution = result.steps[step].distribution(qubits)
    view = top_k(distribution, top)
    labels = [label for label, _ in view.shown]
    values = [prob for _, prob in view.shown]
    if len(view.shown) < view.total_outcomes:
        labels.append(f"Other ({view.total_outcomes - len(view.shown)})")
        values.append(view.remaining_mass)
    fig, ax = plt.subplots(figsize=(max(7, min(20, len(labels) * 0.65)), 4.5))
    ax.bar(range(len(labels)), values)
    ax.set_xticks(range(len(labels)), labels, rotation=50, ha="right")
    ax.set_ylabel("Sampled counts" if sampled else "Exact probability")
    if sampled:
        view_label = "Final measurement counts"
    elif qubits is None and step in (-1, len(result.steps) - 1) and result.circuit.num_clbits:
        view_label = "Final classical-register probabilities"
    else:
        view_label = f"Quantum state after step {result.steps[step].index}"
    ax.set_title(f"{result.circuit.name} | {view_label}")
    if not sampled:
        ax.set_ylim(bottom=0, top=max(1, max(values, default=0) * 1.07))
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    return _save(fig, path)


def plot_circuit(circuit: Circuit, path: str | Path | None = None):
    """Simple static gate timeline; block grouping and GUI editing follow in v0.2."""
    total = len(circuit.operations)
    fig, ax = plt.subplots(figsize=(max(9, min(34, total * 0.53 + 2)),
                                    max(2.5, 0.68 * circuit.num_qubits + 1.4)))
    max_x = total + 0.7
    for q in range(circuit.num_qubits):
        y = circuit.num_qubits - 1 - q
        ax.plot([0.2, max_x], [y, y], linewidth=1, color="#8b97a8")
        ax.text(0.07, y, f"q[{q}]", ha="right", va="center", fontsize=9)
    for col, op in enumerate(circuit.operations, 1):
        ys = [circuit.num_qubits - 1 - q for q in op.qubits]
        if op.name == "BARRIER":
            ax.plot([col, col], [min(ys) - .25, max(ys) + .25],
                    linestyle=":", color="#999999")
        elif op.name in {"CX", "CY", "CZ", "CP"} and len(ys) == 2:
            ax.plot([col, col], ys, color="#415b88", linewidth=1.6)
            ax.scatter([col], [ys[0]], s=30, c="#273b57", zorder=3)
            ax.text(col, ys[1], "⊕" if op.name == "CX" else op.name[-1],
                    ha="center", va="center", fontsize=12, weight="bold",
                    bbox={"boxstyle": "round,pad=0.15", "facecolor": "white",
                          "edgecolor": "#415b88"})
        elif op.name == "MEASURE":
            ax.text(col, ys[0], f"M→c{op.clbit}", ha="center", va="center",
                    fontsize=7, bbox={"boxstyle": "round,pad=0.24",
                                     "facecolor": "#f5dfac", "edgecolor": "#967840"})
        else:
            ax.text(col, np.mean(ys), op.name, ha="center", va="center",
                    fontsize=8, bbox={"boxstyle": "round,pad=0.3",
                                     "facecolor": "#e9eff9", "edgecolor": "#415b88"})
            if len(ys) > 1:
                ax.plot([col, col], [min(ys), max(ys)], zorder=-1, color="#415b88")
    ax.set_xlim(-0.4, total + 1)
    ax.set_ylim(-0.75, circuit.num_qubits - 0.25)
    ax.set_axis_off()
    ax.set_title(circuit.name)
    fig.tight_layout()
    return _save(fig, path)
