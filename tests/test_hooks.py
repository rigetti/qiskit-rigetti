from pyquil import Program

from qiskit_rigetti.hooks.pre_compilation import set_rewiring
from qiskit_rigetti.hooks.pre_execution import enable_active_reset


def test_set_rewiring():
    hook = set_rewiring("NAIVE")
    qasm = "\n".join(
        [
            "OPENQASM 2.0;",
            'include "qelib1.inc";',
        ]
    )

    new_qasm = hook(qasm)

    assert new_qasm.rstrip() == "\n".join(
        [
            "OPENQASM 2.0;",
            '#pragma INITIAL_REWIRING "NAIVE";',
            'include "qelib1.inc";',
        ]
    )


def test_enable_active_reset():
    hook = enable_active_reset
    quil = Program(
        "DECLARE ro BIT[2]",
    )

    new_quil = hook(quil)

    assert new_quil == Program(
        "RESET",
        "DECLARE ro BIT[2]",
    )
