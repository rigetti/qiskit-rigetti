from typing import Callable

from pyquil import Program
from pyquil.gates import RESET

PreExecutionHook = Callable[[Program], Program]
"""Represents a function that can transform a Quil program just before compilation."""


def enable_active_reset(quil: Program) -> Program:
    """
    Enable active reset for all qubits.

    See: https://github.com/quil-lang/quil/blob/master/spec/Quil.md#state-reset for more information.

    :param quil: Quil program to transform.
    :return Copy of the input program, with active reset enabled.
    """
    quil.native_quil_metadata
    return quil.prepend_instructions([RESET()])
