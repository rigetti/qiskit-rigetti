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
from typing import Iterable, Optional, Any, Union, List, cast, Tuple
from uuid import uuid4

from pyquil import get_qc
from pyquil.api import QuantumComputer, QCSClient
from qiskit import QuantumCircuit, ClassicalRegister
from qiskit.circuit import Measure, CircuitInstruction, Clbit
from qiskit.providers import BackendV1, Options, Provider
from qiskit.providers.models import QasmBackendConfiguration
from qiskit.transpiler import CouplingMap
from ._qcs_job import RigettiQCSJob


def _prepare_readouts(circuit: QuantumCircuit) -> None:
    """
    Errors if measuring into more than one readout. If only measuring one, ensures its name is 'ro'. Mutates the input
    circuit.
    """

    measures: List[CircuitInstruction] = [d for d in circuit.data if isinstance(d[0], Measure)]
    readout_names: List[str] = list({clbit.register.name for m in measures for clbit in m.clbits})

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

        def map_ro_reg(clbits: Iterable[Clbit]) -> List[Clbit]:
            return [Clbit(ro_reg, clbit.index) for clbit in clbits if clbit.register.name == orig_readout_name]

        circuit._clbits = map_ro_reg(circuit.clbits)
        circuit._clbit_indices = {
            Clbit(ro_reg, clbit.index): loc._replace(registers=[ro_reg])
            for clbit, loc in circuit._clbit_indices.items()
            if clbit.register.name == orig_readout_name
        }

        for instruction in circuit._data:
            instruction.clbits = map_ro_reg(instruction.clbits)

        break


def _prepare_circuit(circuit: QuantumCircuit) -> QuantumCircuit:
    """
    Returns a prepared copy of the circuit for execution on the QCS Backend.
    """
    circuit = circuit.copy()
    _prepare_readouts(circuit)
    return circuit


class GetQuantumProcessorException(Exception):
    pass


class RigettiQCSBackend(BackendV1):
    """
    Class for representing a Rigetti backend, which may target a real QPU or a simulator.
    """

    def __init__(
        self,
        *,
        compiler_timeout: float,
        execution_timeout: float,
        client_configuration: QCSClient,
        backend_configuration: QasmBackendConfiguration,
        provider: Optional[Provider],
        auto_set_coupling_map: bool = True,
        qc: Optional[QuantumComputer] = None,
        **fields: Any,
    ) -> None:
        """
        Args:
            execution_timeout: Time limit for execution requests, in seconds.
            compiler_timeout: Time limit for compiler requests, in seconds.
            client_configuration: QCS client configuration.
            backend_configuration: Backend configuration.
            provider: Parent provider.
            qc: The `QuantumComputer` this backend represents to Qiskit.
            auto_set_coupling_map: When `True`, this will set the `QasmBackendConfiguration`
                `coupling_map` based on the `QuantumComputer` topology if the existing
                `coupling_map` is empty.
            fields: Keyword arguments for the values to use to override the default options.
        """
        super().__init__(backend_configuration, provider, **fields)
        self._compiler_timeout = compiler_timeout
        self._execution_timeout = execution_timeout
        self._client_configuration = client_configuration
        self._qc = qc
        self._auto_set_coupling_map = auto_set_coupling_map

    @classmethod
    def _default_options(cls) -> Options:
        return Options(shots=None)

    @property
    def qc(self) -> QuantumComputer:
        self._load_qc_if_necessary()
        return cast(QuantumComputer, self._qc)

    @property
    def coupling_map(self) -> CouplingMap:
        self._set_coupling_map_based_on_qc_topology_if_necessary()
        return CouplingMap(self.configuration().coupling_map)

    def _load_qc_if_necessary(self) -> None:
        configuration: QasmBackendConfiguration = self.configuration()
        if self._qc is None:
            try:
                self._qc = get_qc(
                    configuration.backend_name,
                    compiler_timeout=self._compiler_timeout,
                    execution_timeout=self._execution_timeout,
                    client_configuration=self._client_configuration,
                )
            except Exception as e:
                raise GetQuantumProcessorException(
                    f"failed to retrieve quantum processor {configuration.backend_name}"
                ) from e

    def _set_coupling_map_based_on_qc_topology_if_necessary(self) -> None:
        configuration: QasmBackendConfiguration = self.configuration()
        if not configuration.coupling_map and self._auto_set_coupling_map:
            configuration.coupling_map = get_coupling_map_from_qc_topology(self.qc)

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

        self._set_coupling_map_based_on_qc_topology_if_necessary()

        return RigettiQCSJob(
            job_id=str(uuid4()),
            circuits=run_input,
            options=options,
            qc=self.qc,
            backend=self,
            configuration=self.configuration(),
        )


def get_coupling_map_from_qc_topology(qc: QuantumComputer) -> List[Tuple[int, int]]:
    return cast(List[Tuple[int, int]], qc.quantum_processor.qubit_topology().to_directed().edges())
