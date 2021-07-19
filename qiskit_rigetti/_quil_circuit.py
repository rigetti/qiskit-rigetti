##############################################################################
# Copyright 2021 Rigetti Computing
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
##############################################################################
from typing import Any

from qiskit import QuantumCircuit
from qiskit.circuit import InstructionSet

from .gates import (
    CanonicalGate,
    CPhase00Gate,
    CPhase01Gate,
    CPhase10Gate,
    PSwapGate,
    XYGate,
)


class QuilCircuit(QuantumCircuit):
    """
    A :class:`qiskit.circuit.QuantumCircuit` extension with added support for standard Quil gates:

    https://github.com/rigetti/quilc/blob/master/src/quil/stdgates.quil
    """

    def xy(self, theta: float, qubit1: Any, qubit2: Any) -> InstructionSet:
        """Apply :class:`qiskit_rigetti.gates.xy.XYGate`."""
        return self.append(XYGate(theta), [qubit1, qubit2], [])

    def piswap(self, theta: float, qubit1: Any, qubit2: Any) -> InstructionSet:
        """Apply :class:`qiskit_rigetti.gates.xy.XYGate`."""
        return self.xy(theta, qubit1, qubit2)

    def pswap(self, theta: float, qubit1: Any, qubit2: Any) -> InstructionSet:
        """Apply :class:`qiskit_rigetti.gates.pswap.PSwapGate`."""
        return self.append(PSwapGate(theta), [qubit1, qubit2], [])

    def cphase00(self, theta: float, control_qubit: Any, target_qubit: Any) -> InstructionSet:
        """Apply :class:`qiskit_rigetti.gates.cphase.CPhase00`."""
        return self.append(CPhase00Gate(theta), [control_qubit, target_qubit], [])

    def cphase01(self, theta: float, control_qubit: Any, target_qubit: Any) -> InstructionSet:
        """Apply :class:`qiskit_rigetti.gates.cphase.CPhase01`."""
        return self.append(CPhase01Gate(theta), [control_qubit, target_qubit], [])

    def cphase10(self, theta: float, control_qubit: Any, target_qubit: Any) -> InstructionSet:
        """Apply :class:`qiskit_rigetti.gates.cphase.CPhase10`."""
        return self.append(CPhase10Gate(theta), [control_qubit, target_qubit], [])

    def can(self, alpha: float, beta: float, gamma: float, qubit1: Any, qubit2: Any) -> InstructionSet:
        """Apply :class:`qiskit_rigetti.gates.can.CanonicalGate`."""
        return self.append(CanonicalGate(alpha, beta, gamma), [qubit1, qubit2], [])
