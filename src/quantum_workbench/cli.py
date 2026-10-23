"""Command-line demonstrations and file-based acceptance workflow."""

from __future__ import annotations

import argparse
from pathlib import Path

from quantum_workbench import __version__
from quantum_workbench.algorithms import EXAMPLES, make_example
from quantum_workbench.errors import WorkbenchError
from quantum_workbench.execution import Limits, simulate, top_k
from quantum_workbench.export import save_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qworkbench", description="Quantum Computing & Communication Workbench"
    )
    parser.add_argument("--version", action="version", version=f"qworkbench {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("examples", help="List example circuits")
    run = commands.add_parser("run", help="Run and inspect an educational circuit")
    run.add_argument("example", choices=EXAMPLES)
    run.add_argument("--backend", choices=["numpy", "qiskit"], default="numpy")
    run.add_argument("--shots", type=int, default=1024)
    run.add_argument("--seed", type=int, default=42)
    run.add_argument("--top", type=int, default=16, help="Number of outcomes displayed")
    run.add_argument("--all", action="store_true", help="Show every histogram outcome")
    run.add_argument("--num-qubits", type=int, default=3, help="For GHZ or QFT examples")
    run.add_argument("--precision", type=int, default=3, help="For QPE")
    run.add_argument("--phase", type=float, default=0.125, help="For QPE, in turns")
    run.add_argument("--qubits", nargs="+", type=int, help="Display selected quantum marginal")
    run.add_argument("--step", type=int, help="Print probability summary after this step")
    run.add_argument("--branch", type=int, help="Inspect a conditional state branch at --step")
    run.add_argument("--out-dir", type=Path, help="Save JSON, circuit PNG, histograms")
    run.add_argument("--include-amplitudes", action="store_true",
                     help="Include branch statevectors in JSON (larger files)")
    run.add_argument("--max-qubits", type=int, default=12)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "examples":
        for name, description in EXAMPLES.items():
            print(f"{name:<13} {description}")
        return 0
    try:
        circuit = make_example(args.example, num_qubits=args.num_qubits,
                               precision=args.precision, phase=args.phase)
        result = simulate(circuit, shots=args.shots, seed=args.seed,
                          backend=args.backend,
                          limits=Limits(max_qubits=args.max_qubits))
        print(result.summary(limit=None if args.all else args.top))
        if args.step is not None or args.qubits is not None or args.branch is not None:
            index = -1 if args.step is None else args.step
            stage = result.step(index)
            view = top_k(stage.distribution(args.qubits),
                         None if args.all else args.top)
            print(f"\nStep {stage.index}: {stage.operation} | branches={len(stage.branches)}")
            for label, probability in view.shown:
                print(f"  {label}: {probability:.6f}")
            if len(view.shown) != view.total_outcomes:
                print(f"  Other: {view.remaining_mass:.6f}")
            if args.branch is not None:
                branch = stage.branch(args.branch)
                print(f"\nBranch {args.branch}: P={branch.probability:.6f}, "
                      f"classical={branch.classical_label or '(none)'}")
                for basis, amplitude in enumerate(branch.amplitudes):
                    if abs(amplitude) > 1e-10:
                        print(f"  |{basis:0{circuit.num_qubits}b}>: {amplitude:.6g}")
        if args.out_dir:
            import matplotlib.pyplot as plt

            from quantum_workbench.visualize import plot_circuit, plot_probabilities

            args.out_dir.mkdir(parents=True, exist_ok=True)
            save_result(result, args.out_dir / "trace.json",
                        include_amplitudes=args.include_amplitudes,
                        top=None if args.all else args.top)
            fig = plot_circuit(circuit, args.out_dir / "circuit.png")
            plt.close(fig)
            fig = plot_probabilities(result, top=None if args.all else args.top,
                                     qubits=args.qubits, path=args.out_dir / "probabilities.png",
                                     step=-1 if args.step is None else args.step)
            plt.close(fig)
            fig = plot_probabilities(result, sampled=True,
                                     top=None if args.all else args.top,
                                     path=args.out_dir / "counts.png")
            plt.close(fig)
            print(f"\nSaved outputs to {args.out_dir.resolve()}")
        return 0
    except (WorkbenchError, ValueError, RuntimeError, IndexError) as exc:
        build_parser().error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
