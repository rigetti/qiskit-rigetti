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
from typing import Any, Optional, List, Dict

from pyquil.api import QCSClient, list_quantum_computers
from qcs_sdk.qpu.isa import InstructionSetArchitecture, get_instruction_set_architecture, GetISAError
from qiskit.providers import ProviderV1
from qiskit.providers.models import QasmBackendConfiguration

from ._qcs_backend import RigettiQCSBackend, get_coupling_map_from_qc_topology


class RigettiQCSProvider(ProviderV1):
    """
    Class for representing the set of Rigetti backends.
    """

    def __init__(
        self,
        *,
        compiler_timeout: float = 10.0,
        execution_timeout: float = 10.0,
        client_configuration: Optional[QCSClient] = None,
    ) -> None:
        """
        Args:
            execution_timeout: Time limit for execution requests, in seconds.
            compiler_timeout: Time limit for compiler requests, in seconds.
            client_configuration: QCS client configuration. If one is not provided, a default will be loaded.
        """
        super().__init__()
        self._backends: List[RigettiQCSBackend] = []
        self._compiler_timeout = compiler_timeout
        self._execution_timeout = execution_timeout
        self._client_configuration = client_configuration or QCSClient.load()

    def backends(self, name: Optional[str] = None, **__: Any) -> List[RigettiQCSBackend]:
        """
        Get the list of :class:`RigettiQCSBackend` corresponding to the available Quantum Processors.

        Args:
            name: An optional QPU name to match against (e.g. "Aspen-9"). If provided, only matching backends will be
                    returned.

        Returns:
            List[RigettiQCSBackend]: The list of matching backends.
        """
        if not self._backends:
            for qpu, isa in self._get_quantum_processors().items():
                num_qubits = len(isa.architecture.nodes)
                configuration = _configuration(qpu, num_qubits=num_qubits, local=False, simulator=False)
                self._backends.append(
                    RigettiQCSBackend(
                        compiler_timeout=self._compiler_timeout,
                        execution_timeout=self._execution_timeout,
                        client_configuration=self._client_configuration,
                        backend_configuration=configuration,
                        provider=self,
                    )
                )

        if name is None:
            return self._backends
        return [b for b in self._backends if b.name() == name]

    def get_simulator(self, *, num_qubits: int, noisy: bool = False) -> RigettiQCSBackend:
        """
        Get a simulator (QVM).

        Args:
            num_qubits: Number of qubits the simulator should have
            noisy: Whether or not the simulator should simulate noise
        Returns:
            RigettiQCSBackend: A backend representing the simulator
        """
        qvm_url = self._client_configuration.qvm_url
        local = qvm_url == "" or qvm_url.startswith("http://localhost") or qvm_url.startswith("http://127.0.0.1")
        noisy_str = "-noisy" if noisy else ""
        name = f"{num_qubits}q{noisy_str}-qvm"

        configuration = _configuration(name, num_qubits, local=local, simulator=True)
        backend = RigettiQCSBackend(
            compiler_timeout=self._compiler_timeout,
            execution_timeout=self._execution_timeout,
            client_configuration=self._client_configuration,
            backend_configuration=configuration,
            provider=self,
        )
        configuration.coupling_map = get_coupling_map_from_qc_topology(backend.qc)

        return backend

    def _get_quantum_processors(self) -> Dict[str, InstructionSetArchitecture]:
        qpus = list_quantum_computers(qvms=False, client_configuration=self._client_configuration)
        qpu_to_isa: Dict[str, InstructionSetArchitecture] = {}
        for qpu in qpus:
            try:
                qpu_to_isa[qpu] = get_instruction_set_architecture(qpu, client=self._client_configuration)
            except GetISAError:
                pass
        return qpu_to_isa


def _configuration(name: str, num_qubits: int, local: bool, simulator: bool) -> QasmBackendConfiguration:
    return QasmBackendConfiguration(
        backend_name=name,
        backend_version="",
        n_qubits=num_qubits,
        basis_gates=["u1", "u2", "u3", "cx", "id", "cz"],
        gates=[],
        local=local,
        simulator=simulator,
        conditional=False,
        open_pulse=False,
        memory=False,
        max_shots=10000,
        coupling_map=[],
        max_experiments=8,
    )
