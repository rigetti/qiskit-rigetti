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
from qiskit import QuantumRegister
from qiskit.circuit import Qubit

from qiskit_rigetti.gates import (
    CanonicalGate,
    CPhase00Gate,
    CPhase01Gate,
    CPhase10Gate,
    PSwapGate,
    XYGate,
)
from qiskit_rigetti import QuilCircuit


def test_xy():
    circuit = QuilCircuit(2, 2)

    circuit.xy(3.14, 0, 1)

    assert len(circuit.data) == 1
    assert circuit.data[0] == (
        XYGate(3.14),
        [Qubit(QuantumRegister(2, "q"), 0), Qubit(QuantumRegister(2, "q"), 1)],
        [],
    )


def test_piswap():
    circuit = QuilCircuit(2, 2)

    circuit.piswap(3.14, 0, 1)

    assert len(circuit.data) == 1
    assert circuit.data[0] == (
        XYGate(3.14),
        [Qubit(QuantumRegister(2, "q"), 0), Qubit(QuantumRegister(2, "q"), 1)],
        [],
    )


def test_pswap():
    circuit = QuilCircuit(2, 2)

    circuit.pswap(3.14, 0, 1)

    assert len(circuit.data) == 1
    assert circuit.data[0] == (
        PSwapGate(3.14),
        [Qubit(QuantumRegister(2, "q"), 0), Qubit(QuantumRegister(2, "q"), 1)],
        [],
    )


def test_cphase00():
    circuit = QuilCircuit(2, 2)

    circuit.cphase00(3.14, 0, 1)

    assert len(circuit.data) == 1
    assert circuit.data[0] == (
        CPhase00Gate(3.14),
        [Qubit(QuantumRegister(2, "q"), 0), Qubit(QuantumRegister(2, "q"), 1)],
        [],
    )


def test_cphase01():
    circuit = QuilCircuit(2, 2)

    circuit.cphase01(3.14, 0, 1)

    assert len(circuit.data) == 1
    assert circuit.data[0] == (
        CPhase01Gate(3.14),
        [Qubit(QuantumRegister(2, "q"), 0), Qubit(QuantumRegister(2, "q"), 1)],
        [],
    )


def test_cphase10():
    circuit = QuilCircuit(2, 2)

    circuit.cphase10(3.14, 0, 1)

    assert len(circuit.data) == 1
    assert circuit.data[0] == (
        CPhase10Gate(3.14),
        [Qubit(QuantumRegister(2, "q"), 0), Qubit(QuantumRegister(2, "q"), 1)],
        [],
    )


def test_can():
    circuit = QuilCircuit(2, 2)

    circuit.can(3.14, 42.0, 1.62, 0, 1)

    assert len(circuit.data) == 1
    assert circuit.data[0] == (
        CanonicalGate(3.14, 42.0, 1.62),
        [Qubit(QuantumRegister(2, "q"), 0), Qubit(QuantumRegister(2, "q"), 1)],
        [],
    )
