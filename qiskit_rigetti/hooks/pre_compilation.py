from typing import Callable

PreCompilationHook = Callable[[str], str]
"""Represents a function that can transform a QASM program string just before compilation."""


def set_rewiring(rewiring: str) -> PreCompilationHook:
    """
    Create a hook which will apply rewiring before compilation.

    See: https://pyquil-docs.rigetti.com/en/stable/compiler.html#initial-rewiring for more information.

    Args:
        rewiring: Rewiring directive to apply.

    Returns:
        PreCompilationHook: A hook to apply rewiring.

    Examples:
        Applying rewiring to a program::

            >>> from qiskit import execute
            >>> from qiskit_rigetti import RigettiQCSProvider, QuilCircuit
            >>> from qiskit_rigetti.hooks.pre_compilation import set_rewiring

            >>> p = RigettiQCSProvider()
            >>> backend = p.get_simulator(num_qubits=2, noisy=True)
            >>> circuit = QuilCircuit(2, 2)
            >>> _ = circuit.measure([0, 1], [0, 1])
            >>> job = execute(circuit, backend, shots=10, before_compile=[set_rewiring("NAIVE")])
    """

    def fn(qasm: str) -> str:
        return qasm.replace("OPENQASM 2.0;", f'OPENQASM 2.0;\n#pragma INITIAL_REWIRING "{rewiring}";')

    return fn
