import json
import os
import subprocess
import sys

import matplotlib
import pytest

from quantum_workbench import simulate
from quantum_workbench.algorithms import bell
from quantum_workbench.export import result_dict, save_result
from quantum_workbench.visualize import plot_circuit, plot_probabilities

matplotlib.use("Agg")


def test_json_schema_and_optional_amplitudes(tmp_path):
    r = simulate(bell(), seed=123)
    path = save_result(r, tmp_path / "nested" / "trace.json")
    data = json.loads(path.read_text())
    assert data["schema_version"] == 1
    assert data["workbench_version"] == "0.1.0"
    assert data["outcomes"]["probabilities"]["11"] == pytest.approx(.5)
    assert "amplitudes" not in data["steps"][0]["branches"][0]
    verbose = result_dict(r, include_amplitudes=True)
    assert verbose["steps"][0]["branches"][0]["amplitudes"][0] == [1, 0]


def test_matplotlib_artifacts(tmp_path):
    import matplotlib.pyplot as plt

    result = simulate(bell())
    one = plot_circuit(result.circuit, tmp_path / "circuit.svg")
    two = plot_probabilities(result, path=tmp_path / "probabilities.png")
    three = plot_probabilities(result, sampled=True, path=tmp_path / "counts.png")
    for fig in (one, two, three):
        plt.close(fig)
    assert all((tmp_path / name).stat().st_size > 1000 for name in
               ["circuit.svg", "probabilities.png", "counts.png"])
    with pytest.raises(ValueError, match="counts"):
        plot_probabilities(result, sampled=True, qubits=[0])


def test_cli_examples_and_run(tmp_path):
    env = dict(os.environ, MPLBACKEND="Agg")
    examples = subprocess.run(
        [sys.executable, "-m", "quantum_workbench", "examples"],
        capture_output=True, text=True, env=env, check=True,
    )
    assert "uniform" in examples.stdout
    run = subprocess.run(
        [sys.executable, "-m", "quantum_workbench", "run", "qpe",
         "--precision", "3", "--phase", ".125", "--out-dir", str(tmp_path)],
        capture_output=True, text=True, env=env, check=True,
    )
    assert "001" in run.stdout
    assert json.loads((tmp_path / "trace.json").read_text())["outcomes"]["counts"]
    assert (tmp_path / "circuit.png").stat().st_size > 1000


def test_cli_branch_readout():
    env = dict(os.environ, MPLBACKEND="Agg")
    run = subprocess.run(
        [sys.executable, "-m", "quantum_workbench", "run", "measurement",
         "--step", "3", "--branch", "1"],
        capture_output=True, text=True, env=env, check=True,
    )
    assert "Branch 1: P=0.500000" in run.stdout
    assert "|11>" in run.stdout


def test_version_is_single_source():
    from quantum_workbench import __version__
    from quantum_workbench._version import __version__ as authoritative
    assert __version__ == authoritative == "0.1.0"


def test_qpe_final_plot_uses_classical_register_not_work_qubit():
    import matplotlib.pyplot as plt

    from quantum_workbench.algorithms import qpe

    result = simulate(qpe(3, 0.125))
    fig = plot_probabilities(result)
    try:
        labels = [item.get_text() for item in fig.axes[0].get_xticklabels()]
        assert "001" in labels
        assert "1001" not in labels
        assert "classical-register" in fig.axes[0].get_title()
    finally:
        plt.close(fig)
