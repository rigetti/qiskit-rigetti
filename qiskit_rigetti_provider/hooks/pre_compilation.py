from typing import Callable

PreCompilationHook = Callable[[str], str]
"""Represents a function that can transform a QASM program string just before compilation."""


def set_rewiring(rewiring: str) -> PreCompilationHook:
    """
    Set compiler directive for rewiring.

    See: https://pyquil-docs.rigetti.com/en/stable/compiler.html#initial-rewiring for more information.

    :param rewiring: Rewiring directive to apply.
    :return A QASM 2.0 string including the rewiring directive.
    """

    def fn(qasm: str) -> str:
        return qasm.replace("OPENQASM 2.0;", f'OPENQASM 2.0;\n#pragma INITIAL_REWIRING "{rewiring}"')

    return fn
