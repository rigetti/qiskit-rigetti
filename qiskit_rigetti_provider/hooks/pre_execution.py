from typing import Callable, Dict, Any

from pyquil import Program
from pyquil.gates import RESET

PreExecutionHook = Callable[[Program, Dict[str, Any]], Program]
"""Represents a function that can transform a Quil program just before execution."""


def enable_active_reset(quil: Program, **kwargs: Any) -> Program:
    """
    Enable active reset for all qubits.

    See: https://github.com/quil-lang/quil/blob/master/spec/Quil.md#state-reset for more information.

    :param quil: Quil program to transform.
    :return Copy of the input program, with active reset enabled.
    """
    return quil.prepend_instructions([RESET()])
