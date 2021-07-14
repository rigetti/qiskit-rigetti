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

Response = Union[QVMExecuteResponse, QPUExecuteResponse]


class RigettiQCSJob(JobV1):
    """
    Class for representing execution jobs sent to Rigetti backends.
    """

    def __init__(
        self,
        job_id: str,
        circuits: List[QuantumCircuit],
        options: Dict[str, Any],
        qc: QuantumComputer,
        backend: Backend,
        configuration: QasmBackendConfiguration,
    ) -> None:
        """
        Create new job.

        :param job_id: unique identifier for this job
        :param circuits: list of circuits to execute
        :param options: execution options (e.g. "shots")
        :param qc: quantum computer to run against
        :param backend: backend that created this job
        :param configuration: configuration from parent backend
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
        Not implemented for this class as it uses the asynchronous pattern

        :raises NotImplementedError:
        """
        raise NotImplementedError("'submit' is not implemented as this class uses the asynchronous pattern")

    def _start(self) -> None:
        self._responses = [self._start_circuit(circuit) for circuit in self._circuits]
        self._status = JobStatus.RUNNING

    def _start_circuit(self, circuit: QuantumCircuit) -> Response:
        shots = self._options["shots"]
        qasm = circuit.qasm()

        # TODO (andrew):
        # - Support sequences of hooks
        # - Support recompilation when needed

        before_compile = self._options.get("before_compile")
        if before_compile is not None:
            qasm = before_compile(qasm)

        program = Program(RawInstr(qasm)).wrap_in_numshots_loop(shots)
        native_program = self._qc.compiler.quil_to_native_quil(program)

        before_execute = self._options.get("before_execute")
        if before_execute is not None:
            native_program = before_execute(native_program)

        compiled = self._qc.compiler.native_quil_to_executable(native_program)

        # typing: QuantumComputer's inner QAM is generic, so we set the expected type here
        return cast(Response, self._qc.qam.execute(compiled))

    def result(self) -> Result:
        """
        Wait until the job is complete, then return a result.

        :raises JobError: if there was a problem running the Job or retrieving the result
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
        Attempt to cancel this job. Because this job implementation is synchronous, calling
        this method will always raise a ``NotImplementedError``.

        :raises NotImplementedError:
        """
        raise NotImplementedError("Cancelling jobs is not supported")

    def status(self) -> JobStatus:
        """Get the current status of this Job"""

        return self._status


def _to_binary_str(state: List[int]) -> str:
    # NOTE: According to https://arxiv.org/pdf/1809.03452.pdf, this should be a hex string
    # but it results in missing leading zeros in the displayed output, and binary strings
    # seem to work too. Hex string could be accomplished with:
    #     hex(int(binary_str, 2))
    binary_str = "".join(map(str, state[::-1]))
    return binary_str
