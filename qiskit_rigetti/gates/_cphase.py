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
__all__ = [
    "CPhase00Gate",
    "CPhase01Gate",
    "CPhase10Gate",
]

from pyquil.simulation.matrices import CPHASE00, CPHASE01, CPHASE10
from qiskit.extensions import UnitaryGate


class CPhase00Gate(UnitaryGate):
    """
    Class for representing a CPhase00 gate, a variant of CPhase that affects state ``|00>``

    ::

        CPHASE00(theta) = [[exp(i*theta), 0, 0, 0],
                           [0,            1, 0, 0],
                           [0,            0, 1, 0],
                           [0,            0, 0, 1]]

    """

    def __init__(self, theta: float):
        """
        Args:
            theta: Phase angle
        """
        super().__init__(CPHASE00(theta), "cphase00")


class CPhase01Gate(UnitaryGate):
    """
    Class for representing a CPhase01 gate, a variant of CPhase that affects state ``|01>``

    ::

        CPHASE01(theta) = [[1, 0,            0, 0],
                           [0, exp(i*theta), 0, 0],
                           [0, 0,            1, 0],
                           [0, 0,            0, 1]]
    """

    def __init__(self, theta: float):
        """
        Args:
            theta: Phase angle
        """
        super().__init__(CPHASE01(theta), "cphase01")


class CPhase10Gate(UnitaryGate):
    """
    Class for representing a CPhase10 gate, a variant of CPhase that affects state ``|10>``

    ::

        CPHASE01(theta) = [[1, 0, 0,            0],
                           [0, 1, 0,            0],
                           [0, 0, exp(i*theta), 0],
                           [0, 0, 0,            1]]
    """

    def __init__(self, theta: float):
        """
        Args:
            theta: Phase angle
        """
        super().__init__(CPHASE10(theta), "cphase10")
