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
import warnings
from collections import Counter
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, Iterator, cast

import numpy as np
from dateutil.tz import tzutc
from pyquil import Program
from pyquil.api import QuantumComputer
from pyquil.api._qpu import QPUExecuteResponse
from pyquil.api._qvm import QVMExecuteResponse
from pyquil.quilbase import RawInstr
from qiskit import QuantumCircuit
from qiskit.providers import JobStatus, JobV1, Backend
from qiskit.providers.models import QasmBackendConfiguration
from qiskit.qobj import QobjExperimentHeader
from qiskit.result import Result
from qiskit.result.models import ExperimentResult, ExperimentResultData

from .hooks.pre_compilation import PreCompilationHook
from .hooks.pre_execution import PreExecutionHook

Response = Union[QVMExecuteResponse, QPUExecuteResponse]


class RigettiQCSJob(JobV1):
    """
    Class for representing execution jobs sent to Rigetti backends.
    """

    def __init__(
        self,
        *,
        job_id: str,
        circuits: List[QuantumCircuit],
        options: Dict[str, Any],
        qc: QuantumComputer,
        backend: Backend,
        configuration: QasmBackendConfiguration,
    ) -> None:
        """
        Args:
            job_id: Unique identifier for this job
            circuits: List of circuits to execute
            options: Execution options (e.g. "shots")
            qc: Quantum computer to run against
            backend: :class:`RigettiQCSBackend` that created this job
            configuration: Configuration from parent backend
        """
        super().__init__(backend, job_id)

        self._status = JobStatus.INITIALIZING
        self._circuits = circuits
        self._options = options
        self._qc = qc
        self._configuration = configuration
        self._result: Optional[Result] = None
        self._responses: List[Response] = []

        self._start()

    def submit(self) -> None:
        """
        Raises:
            NotImplementedError: This class uses the asynchronous pattern, so this method should not be called.
        """
        raise NotImplementedError("'submit' is not implemented as this class uses the asynchronous pattern")

    def _start(self) -> None:
        self._responses = [self._start_circuit(circuit) for circuit in self._circuits]
        self._status = JobStatus.RUNNING

    def _start_circuit(self, circuit: QuantumCircuit) -> Response:
        shots = self._options["shots"]
        qasm = circuit.qasm()
        qasm = self._handle_barriers(qasm, circuit.num_qubits)

        before_compile: List[PreCompilationHook] = self._options.get("before_compile", [])
        for fn in before_compile:
            qasm = fn(qasm)

        program = Program(RawInstr(qasm)).wrap_in_numshots_loop(shots)
        program = self._qc.compiler.quil_to_native_quil(program)

        before_execute: List[PreExecutionHook] = self._options.get("before_execute", [])
        for fn in before_execute:
            program = fn(program)

        if self._options.get("ensure_native_quil") and len(before_execute) > 0:
            program = self._qc.compiler.quil_to_native_quil(program)

        executable = self._qc.compiler.native_quil_to_executable(program)

        # typing: QuantumComputer's inner QAM is generic, so we set the expected type here
        return cast(Response, self._qc.qam.execute(executable))

    @staticmethod
    def _handle_barriers(qasm: str, num_circuit_qubits: int) -> str:
        lines = []
        for line in qasm.splitlines():
            if line.startswith("barrier"):
                warnings.warn("barriers are currently omitted during execution on a RigettiQCSBackend")
                continue

            lines.append(line)
        return "\n".join(lines)

    def result(self) -> Result:
        """
        Wait until the job is complete, then return a result.

        Raises:
            JobError: If there was a problem running the Job or retrieving the result
        """
        if self._result is not None:
            return self._result

        now = datetime.now(tzutc())

        results = []
        success = True
        for r in self._get_experiment_results():
            results.append(r)
            success &= r.success

        self._result = Result(
            backend_name=self._configuration.backend_name,
            backend_version=self._configuration.backend_version,
            qobj_id="",
            job_id=self.job_id(),
            success=success,
            results=results,
            date=now,
        )

        self._status = JobStatus.DONE if success else JobStatus.ERROR
        return self._result

    def _get_experiment_results(self) -> Iterator[ExperimentResult]:
        shots = self._options["shots"]

        for circuit_idx, response in enumerate(self._responses):
            states = self._qc.qam.get_result(response).readout_data["ro"]
            memory = list(map(_to_binary_str, np.array(states)))
            success = True
            status = "Completed successfully"

            circuit = self._circuits[circuit_idx]
            yield ExperimentResult(
                header=QobjExperimentHeader(name=circuit.name),
                shots=shots,
                success=success,
                status=status,
                data=ExperimentResultData(counts=Counter(memory), memory=memory),
            )

    def cancel(self) -> None:
        """
        Raises:
            NotImplementedError: There is currently no way to cancel this job.
        """
        raise NotImplementedError("Cancelling jobs is not supported")

    def status(self) -> JobStatus:
        """Get the current status of this Job

        If this job was RUNNING when you called it, this function will block until the job is complete.
        """

        if self._status == JobStatus.RUNNING:
            # Wait for results _now_ to finish running, otherwise consuming code might wait forever.
            self.result()

        return self._status


def _to_binary_str(state: List[int]) -> str:
    # NOTE: According to https://arxiv.org/pdf/1809.03452.pdf, this should be a hex string
    # but it results in missing leading zeros in the displayed output, and binary strings
    # seem to work too. Hex string could be accomplished with:
    #     hex(int(binary_str, 2))
    binary_str = "".join(map(str, state[::-1]))
    return binary_str
