"""Versioned, reproducible, machine-readable result exports.

Only trusted local scripts create circuits; JSON files are pure data and are
never evaluated as Python. Snapshots are available as real/imag arrays.
"""

from __future__ import annotations

import json
from pathlib import Path

from quantum_workbench import __version__
from quantum_workbench.execution import RunResult


def result_dict(result: RunResult, *, include_amplitudes: bool = False,
                top: int | None = 16) -> dict:
    from quantum_workbench.execution import top_k

    snapshots = []
    for step in result.steps:
        view = top_k(step.distribution(), top)
        data = {
            "step": step.index,
            "operation": step.operation,
            "qubits": list(step.qubits),
            "block": step.block,
            "branch_count": len(step.branches),
            "top_probabilities": dict(view.shown),
            "remaining_mass": view.remaining_mass,
            "total_outcomes": view.total_outcomes,
        }
        if include_amplitudes:
            data["branches"] = [
                {
                    "probability": branch.probability,
                    "classical_bits": branch.classical_label,
                    "amplitudes": [[float(z.real), float(z.imag)]
                                   for z in branch.amplitudes],
                }
                for branch in step.branches
            ]
        else:
            data["branches"] = [
                {"probability": b.probability, "classical_bits": b.classical_label}
                for b in step.branches
            ]
        snapshots.append(data)
    return {
        "schema_version": 1,
        "workbench_version": __version__,
        "backend": result.backend,
        "seed": result.seed,
        "shots": result.shots,
        "circuit": {
            "name": result.circuit.name,
            "num_qubits": result.circuit.num_qubits,
            "num_clbits": result.circuit.num_clbits,
            "global_phase": result.circuit.global_phase,
            "operations": [
                {"name": op.name, "qubits": list(op.qubits), "clbit": op.clbit,
                 "block": op.block, "parameters": list(op.parameters)}
                for op in result.circuit.operations
            ],
        },
        "outcomes": {
            "kind": result.outcome_kind,
            "probabilities": result.outcome_probabilities,
            "counts": result.counts,
        },
        "steps": snapshots,
    }


def save_result(result: RunResult, path: str | Path, *, include_amplitudes: bool = False,
                top: int | None = 16) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result_dict(result, include_amplitudes=include_amplitudes, top=top),
                   indent=2) + "\n", encoding="utf-8"
    )
    return destination
