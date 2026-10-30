"""Acceptance example: dynamic if_test must fail loudly during import.

Run from repository root:
    uv run python examples/acceptance_qiskit_control_flow.py
An expected rejection is a PASS; silently accepting the circuit is a failure.
"""

from qiskit import QuantumCircuit

from quantum_workbench.errors import UnsupportedOperationError
from quantum_workbench.qiskit_adapter import from_qiskit


def main() -> None:
    qc = QuantumCircuit(1, 1, name="Unsupported dynamic control")
    qc.h(0)
    qc.measure(0, 0)
    with qc.if_test((qc.clbits[0], 1)):
        qc.x(0)

    print(qc.draw(output="text"))
    print("Qiskit instruction names:", [instruction.operation.name for instruction in qc.data])
    try:
        from_qiskit(qc)
    except UnsupportedOperationError as exc:
        message = str(exc)
        if "if_else" not in message or "control flow" not in message:
            raise AssertionError(f"Rejection was not specific enough: {message}") from exc
        print(f"\nPASS: safely rejected dynamic circuit:\n  {message}")
    else:
        raise AssertionError("FAIL: importer accepted a dynamic if_test circuit!")


if __name__ == "__main__":
    main()
