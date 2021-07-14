from qiskit import execute
from qiskit_rigetti_provider import RigettiQCSProvider, QuilCircuit
from pyquil import Program


def test_execute__basic_circuit():
    """Tests example from README"""
    p = RigettiQCSProvider()
    backend = p.get_simulator(num_qubits=2, noisy=False)

    circuit = QuilCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])

    job = execute(circuit, backend, shots=10)
    result = job.result()

    assert result.get_counts().keys() == {"00", "11"}


def test_execute__circuit_with_lifecycle_hooks():
    """Tests hooks integration"""
    p = RigettiQCSProvider()
    backend = p.get_simulator(num_qubits=2, noisy=False)

    circuit = QuilCircuit(2, 2)
    circuit.h(0)
    circuit.measure([0, 1], [0, 1])

    def pre_compilation_hook(qasm: str) -> str:
        assert qasm.rstrip() == "\n".join(
            [
                "OPENQASM 2.0;",
                'include "qelib1.inc";',
                "qreg q[2];",
                "creg ro[2];",
                "u2(0,pi) q[0];",
                "measure q[0] -> ro[0];",
                "measure q[1] -> ro[1];",
            ]
        )
        return "\n".join(
            [
                "OPENQASM 2.0;",
                'include "qelib1.inc";',
                "qreg q[2];",
                "creg ro[2];",
                "measure q[0] -> ro[0];",
                "measure q[1] -> ro[1];",
            ]
        )

    def pre_execution_hook(quil: Program) -> Program:
        assert quil == Program(
            "DECLARE ro BIT[2]",
            "MEASURE 1 ro[1]",
            "MEASURE 0 ro[0]",
        )
        return Program(
            "DECLARE ro BIT[1]",
            "X 0",
            "MEASURE 0 ro[0]",
        )

    job = execute(circuit, backend, shots=10, before_compile=pre_compilation_hook, before_execute=pre_execution_hook)
    result = job.result()

    assert result.get_counts().keys() == {"1"}
