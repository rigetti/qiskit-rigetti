from typing import Callable

from pyquil import Program
from pyquil.gates import RESET

PreExecutionHook = Callable[[Program], Program]
"""Represents a function that can transform a Quil program just before execution."""


def enable_active_reset(quil: Program) -> Program:
    """
    Enable active reset for all qubits.

    See: https://github.com/quil-lang/quil/blob/master/spec/Quil.md#state-reset for more information.

    Args:
        quil: Quil program to transform.

    Returns:
        Copy of the input program, with active reset enabled.
    """
    return quil.prepend_instructions([RESET()])
