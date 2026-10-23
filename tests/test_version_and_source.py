import tomllib
from pathlib import Path

from quantum_workbench import __version__
from quantum_workbench.circuits import Circuit


def test_hatch_reads_single_authoritative_version():
    pyproject = tomllib.loads(Path("pyproject.toml").read_text())
    assert pyproject["project"]["dynamic"] == ["version"]
    assert pyproject["tool"]["hatch"]["version"]["path"] == \
        "src/quantum_workbench/_version.py"
    assert __version__ == "0.1.0"


def test_composite_gate_parameters_survive_mapping():
    child = Circuit(2).cp(0.75, 0, 1)
    parent = Circuit(3).append(child, [2, 0], label="Controlled phase")
    assert parent.operations[0].parameters == (0.75,)
    assert parent.operations[0].qubits == (2, 0)
