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
__all__ = ["PSwapGate"]

from pyquil.simulation.matrices import PSWAP
from qiskit.extensions import UnitaryGate


class PSwapGate(UnitaryGate):
    """
    Class for representing a parametric Swap gate

    ::

        PSWAP(theta) = [[1, 0,              0,              0],
                        [0, 0,              exp(i * theta), 0],
                        [0, exp(i * theta), 0,              0],
                        [0, 0,              0,              1]]
    """

    def __init__(self, theta: float):
        """
        Args:
            theta: Phase angle
        """
        super().__init__(PSWAP(theta), "pswap")
