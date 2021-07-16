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
__all__ = ["CanonicalGate"]

import numpy as np
from qiskit.extensions import UnitaryGate


class CanonicalGate(UnitaryGate):
    """
    Class for representing a canonical gate

    ::

        CAN(alpha, beta, gamma) = [[(exp(i*(alpha+beta-gamma)/2)+exp(i*(alpha-beta+gamma)/2))/2, 0,                                                                    0,                                                                    (exp(i*(alpha-beta+gamma)/2)-exp(i*(alpha+beta-gamma)/2))/2],
                                   [0,                                                                 (exp(i*(alpha+beta+gamma)/(-2))+exp(i*(beta+gamma-alpha)/2))/2, (exp(i*(alpha+beta+gamma)/(-2))-exp(i*(beta+gamma-alpha)/2))/2, 0                                                                ],
                                   [0,                                                                 (exp(i*(alpha+beta+gamma)/(-2))-exp(i*(beta+gamma-alpha)/2))/2, (exp(i*(alpha+beta+gamma)/(-2))+exp(i*(beta+gamma-alpha)/2))/2, 0                                                                ],
                                   [(exp(i*(alpha-beta+gamma)/2)-exp(i*(alpha+beta-gamma)/2))/2, 0,                                                                    0,                                                                    (exp(i*(alpha+beta-gamma)/2)+exp(i*(alpha-beta+gamma)/2))/2]]

    """  # noqa: E501

    def __init__(self, alpha: float, beta: float, gamma: float):
        """
        Args:
            alpha: X-axis phase angle
            beta: Y-axis phase angle
            gamma: Z-axis phase angle
        """
        # fmt: off
        super().__init__(
            np.array([[(np.exp(1j * (alpha + beta - gamma) / 2) + np.exp(1j * (alpha - beta + gamma) / 2)) / 2, 0,                                                                                          0,                                                                                          (np.exp(1j * (alpha - beta + gamma) / 2) - np.exp(1j * (alpha + beta - gamma) / 2)) / 2],    # noqa: E501, E241, E202
                      [0,                                                                                       (np.exp(1j * (alpha + beta + gamma) / (-2)) + np.exp(1j * (beta + gamma - alpha) / 2)) / 2, (np.exp(1j * (alpha + beta + gamma) / (-2)) - np.exp(1j * (beta + gamma - alpha) / 2)) / 2, 0                                                                                      ],    # noqa: E501, E241, E202
                      [0,                                                                                       (np.exp(1j * (alpha + beta + gamma) / (-2)) - np.exp(1j * (beta + gamma - alpha) / 2)) / 2, (np.exp(1j * (alpha + beta + gamma) / (-2)) + np.exp(1j * (beta + gamma - alpha) / 2)) / 2, 0                                                                                      ],    # noqa: E501, E241, E202
                      [(np.exp(1j * (alpha - beta + gamma) / 2) - np.exp(1j * (alpha + beta - gamma) / 2)) / 2, 0,                                                                                          0,                                                                                          (np.exp(1j * (alpha + beta - gamma) / 2) + np.exp(1j * (alpha - beta + gamma) / 2)) / 2]]),  # noqa: E501, E241, E202
            "can"
        )
        # fmt: on
