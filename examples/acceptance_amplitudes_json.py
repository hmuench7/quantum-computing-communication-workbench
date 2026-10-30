"""Acceptance example: inspect CLI --include-amplitudes JSON without flooding stdout.

Run from repository root:
    uv run python examples/acceptance_amplitudes_json.py
Creates outputs/acceptance-json/, which is ignored by the project's gitignore.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path("outputs/acceptance-json")


def run_cli(name: str, n: int, include_amplitudes: bool) -> tuple[Path, dict]:
    destination = ROOT / f"{name}-{n}q-{'expanded' if include_amplitudes else 'compact'}"
    arguments = [
        sys.executable, "-m", "quantum_workbench", "run", name,
        "--num-qubits", str(n), "--out-dir", str(destination), "--shots", "1024",
    ]
    if include_amplitudes:
        arguments.append("--include-amplitudes")
    env = dict(os.environ, MPLBACKEND="Agg")
    subprocess.run(arguments, check=True, text=True, capture_output=True, env=env)
    path = destination / "trace.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def validate(name: str, n: int) -> None:
    small_file, small = run_cli(name, n, False)
    large_file, large = run_cli(name, n, True)
    assert small["schema_version"] == large["schema_version"] == 1
    assert small["outcomes"] == large["outcomes"]
    assert len(small["steps"]) == len(large["steps"])
    assert all("amplitudes" not in branch for step in small["steps"]
               for branch in step["branches"])

    for step in large["steps"]:
        assert abs(sum(branch["probability"] for branch in step["branches"]) - 1) < 1e-9
        for branch in step["branches"]:
            array = np.asarray(branch["amplitudes"], dtype=float)
            assert array.shape == (1 << n, 2)  # [real, imag] per basis state
            assert np.isfinite(array).all()
            assert abs(float(np.sum(array**2)) - 1) < 1e-9

    compact_bytes = small_file.stat().st_size
    expanded_bytes = large_file.stat().st_size
    assert expanded_bytes > compact_bytes
    print(f"{name}-{n}q: {len(large['steps'])} steps, "
          f"{compact_bytes:,} B compact vs {expanded_bytes:,} B expanded "
          f"({expanded_bytes / compact_bytes:.1f}x)")
    print("  First step JSON keys:", list(large["steps"][0]))
    print("  Branch JSON keys:", list(large["steps"][0]["branches"][0]))

    if name == "bell":
        # INITIAL, H, CX, then the two measurements.
        prepared = large["steps"][2]["branches"][0]["amplitudes"]
        print("  State after H,CX (nonzero basis amplitudes):")
        for index, (real, imag) in enumerate(prepared):
            if real * real + imag * imag > 1e-15:
                print(f"    |{index:02b}>: {real:+.8f}{imag:+.8f}j")
    print("  PASS: readable JSON, normalized branches, probabilities unchanged\n")


def main() -> None:
    validate("bell", 2)
    validate("uniform", 7)
    print(f"JSON and PNG outputs are in {ROOT.resolve()}")


if __name__ == "__main__":
    main()
