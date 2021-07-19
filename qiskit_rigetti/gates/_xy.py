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
__all__ = ["XYGate"]

from pyquil.simulation.matrices import XY
from qiskit.extensions import UnitaryGate


class XYGate(UnitaryGate):
    """
    Class for representing an XY gate (parametric iSwap gate)

    ::

        XY(theta) = [[1, 0,                0,                0],
                     [0, cos(theta/2),     i * sin(theta/2), 0],
                     [0, i * sin(theta/2), cos(theta/2),     0],
                     [0, 0,                0,                1]]

    See https://arxiv.org/pdf/1912.04424.pdf for technical details.
    """

    def __init__(self, theta: float):
        """
        Args:
            theta: Phase angle
        """
        super().__init__(XY(theta), "xy")
