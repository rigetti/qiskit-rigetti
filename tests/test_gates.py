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
import numpy as np
from numpy.testing import assert_allclose

from qiskit_rigetti.gates import (
    CanonicalGate,
    CPhase00Gate,
    CPhase01Gate,
    CPhase10Gate,
    PSwapGate,
    XYGate,
)


def test_xy_gate():
    theta = 3.14
    # fmt: off
    assert_allclose(
        XYGate(theta).to_matrix(),
        np.array([[1, 0,                    0,                    0],
                  [0, np.cos(theta/2),      1j * np.sin(theta/2), 0],
                  [0, 1j * np.sin(theta/2), np.cos(theta/2),      0],
                  [0, 0,                    0,                    1]])
    )
    # fmt: on


def test_pswap_gate():
    theta = 3.14
    # fmt: off
    assert_allclose(
        PSwapGate(theta).to_matrix(),
        np.array([[1, 0,                  0,                  0],
                  [0, 0,                  np.exp(1j * theta), 0],
                  [0, np.exp(1j * theta), 0,                  0],
                  [0, 0,                  0,                  1]])
    )
    # fmt: on


def test_cphase00_gate():
    theta = 3.14
    assert_allclose(CPhase00Gate(theta).to_matrix(), np.diag([np.exp(1j * theta), 1.0, 1.0, 1.0]))


def test_cphase01_gate():
    theta = 3.14
    assert_allclose(CPhase01Gate(theta).to_matrix(), np.diag([1.0, np.exp(1j * theta), 1.0, 1.0]))


def test_cphase10_gate():
    theta = 3.14
    assert_allclose(CPhase10Gate(theta).to_matrix(), np.diag([1.0, 1.0, np.exp(1j * theta), 1.0]))


def test_canonical_gate():
    alpha = 3.14
    beta = 42.0
    gamma = 1.62
    # fmt: off
    assert_allclose(
        CanonicalGate(alpha, beta, gamma).to_matrix(),
        np.array([[(np.exp(1j*(alpha+beta-gamma)/2)+np.exp(1j*(alpha-beta+gamma)/2))/2, 0,                                                                      0,                                                                      (np.exp(1j*(alpha-beta+gamma)/2)-np.exp(1j*(alpha+beta-gamma)/2))/2],
                  [0,                                                                   (np.exp(1j*(alpha+beta+gamma)/(-2))+np.exp(1j*(beta+gamma-alpha)/2))/2, (np.exp(1j*(alpha+beta+gamma)/(-2))-np.exp(1j*(beta+gamma-alpha)/2))/2, 0                                                                ],
                  [0,                                                                   (np.exp(1j*(alpha+beta+gamma)/(-2))-np.exp(1j*(beta+gamma-alpha)/2))/2, (np.exp(1j*(alpha+beta+gamma)/(-2))+np.exp(1j*(beta+gamma-alpha)/2))/2, 0                                                                ],
                  [(np.exp(1j*(alpha-beta+gamma)/2)-np.exp(1j*(alpha+beta-gamma)/2))/2, 0,                                                                      0,                                                                      (np.exp(1j*(alpha+beta-gamma)/2)+np.exp(1j*(alpha-beta+gamma)/2))/2]]),

    )
    # fmt: on
