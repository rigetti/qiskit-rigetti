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
from typing import Optional, Any, Union, List
from uuid import uuid4

from pyquil import get_qc
from pyquil.api import QuantumComputer, EngagementManager
from qcs_api_client.client import QCSClientConfiguration
from qiskit import QuantumCircuit, ClassicalRegister
from qiskit.circuit import Measure
from qiskit.providers import BackendV1, Options, Provider
from qiskit.providers.models import QasmBackendConfiguration

from ._qcs_job import RigettiQCSJob


def _prepare_readouts(circuit: QuantumCircuit) -> None:
    """
    Errors if measuring into more than one readout. If only measuring one, ensures its name is 'ro'. Mutates the input
    circuit.
    """

    # cache register locations for each bit in circuit
    bit_info = {bit: {"reg": reg, "idx": i} for reg in circuit.cregs for i, bit in enumerate(reg)}

    # NOTE: each measure is a tuple of the form (measure, qubits, classical bits)
    measures = [d for d in circuit.data if isinstance(d[0], Measure)]
    readout_names = list({bit_info[clbit]["reg"].name for m in measures for clbit in m[2]})
    num_readouts = len(readout_names)

    if num_readouts == 0:
        raise RuntimeError("Circuit has no measurements")

    if num_readouts > 1:
        readout_names.sort()
        raise RuntimeError(
            f"Multiple readout registers are unsupported on QCSBackend; found {', '.join(readout_names)}"
        )

    orig_readout_name = readout_names[0]
    if orig_readout_name == "ro":
        return

    for i, reg in enumerate(circuit.cregs):
        if reg.name != orig_readout_name:
            continue

        # rename register to "ro"
        ro_reg = ClassicalRegister(size=reg.size, name="ro")
        circuit.cregs[i] = ro_reg

        # fix classical bit references in circuit
        for i, clbit in enumerate(circuit.clbits):
            orig_reg = bit_info[clbit]["reg"]
            if orig_reg.name == orig_readout_name:
                idx = bit_info[clbit]["idx"]
                circuit.clbits[i] = ro_reg[idx]

        # fix classical bit references in measures
        for m in measures:
            for i, clbit in enumerate(m[2]):
                orig_reg = bit_info[clbit]["reg"]
                if orig_reg.name == orig_readout_name:
                    idx = bit_info[clbit]["idx"]
                    m[2][i] = ro_reg[idx]
        break


def _prepare_circuit(circuit: QuantumCircuit) -> QuantumCircuit:
    """
    Returns a prepared copy of the circuit for execution on the QCS Backend.
    """
    circuit = circuit.copy()
    _prepare_readouts(circuit)
    return circuit


class RigettiQCSBackend(BackendV1):
    """
    Class for representing a Rigetti backend, which may target a real QPU or a simulator.
    """

    def __init__(
        self,
        *,
        compiler_timeout: float,
        execution_timeout: float,
        client_configuration: QCSClientConfiguration,
        engagement_manager: EngagementManager,
        backend_configuration: QasmBackendConfiguration,
        provider: Optional[Provider],
        **fields: Any,
    ) -> None:
        """
        Args:
            execution_timeout: Time limit for execution requests, in seconds.
            compiler_timeout: Time limit for compiler requests, in seconds.
            client_configuration: QCS client configuration.
            engagement_manager: QPU engagement manager.
            backend_configuration: Backend configuration.
            provider: Parent provider.
            fields: Keyword arguments for the values to use to override the default options.
        """
        super().__init__(backend_configuration, provider, **fields)
        self._compiler_timeout = compiler_timeout
        self._execution_timeout = execution_timeout
        self._client_configuration = client_configuration
        self._engagement_manager = engagement_manager
        self._qc: Optional[QuantumComputer] = None

    @classmethod
    def _default_options(cls) -> Options:
        return Options(shots=None)

    def run(
        self,
        run_input: Union[QuantumCircuit, List[QuantumCircuit]],
        **options: Any,
    ) -> RigettiQCSJob:
        """
        Run the quantum circuit(s) using this backend.

        Args:
            run_input: Either a single :class:`QuantumCircuit` to run or a list of them to run in parallel.
            **options: Execution options to forward to :class:`RigettiQCSJob`.

        Returns:
            RigettiQCSJob: The job that has been started. Wait for it by calling :func:`RigettiQCSJob.result`
        """
        if not isinstance(run_input, list):
            run_input = [run_input]

        bindings = options.get("parameter_binds") or []
        if len(bindings) > 0:
            run_input = [circuit.bind_parameters(binding) for circuit in run_input for binding in bindings]

        run_input = [_prepare_circuit(circuit) for circuit in run_input]

        if self._qc is None:
            self._qc = get_qc(
                self.configuration().backend_name,
                compiler_timeout=self._compiler_timeout,
                execution_timeout=self._execution_timeout,
                client_configuration=self._client_configuration,
                engagement_manager=self._engagement_manager,
            )

        return RigettiQCSJob(
            job_id=str(uuid4()),
            circuits=run_input,
            options=options,
            qc=self._qc,
            backend=self,
            configuration=self.configuration(),
        )
