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
from typing import Optional

import pytest
from pyquil import get_qc, Program
from pyquil.api import QuantumComputer
from pytest_mock import MockerFixture
from qiskit import QuantumRegister, ClassicalRegister
from qiskit.providers import JobStatus

from qiskit_rigetti_provider import RigettiQCSJob, RigettiQCSProvider, RigettiQCSBackend, QuilCircuit


def test_init__start_circuit_unsuccessful(backend: RigettiQCSBackend):
    circuit = make_circuit(2 * backend.configuration().num_qubits)  # Use too many qubits
    with pytest.raises(Exception):
        make_job(backend, circuit)


def test_init__circuit_with_rewiring(backend: RigettiQCSBackend, mocker: MockerFixture):
    circuit = make_circuit(backend.configuration().num_qubits)
    circuit.set_rewiring("NAIVE")
    qc = get_qc(backend.configuration().backend_name)
    quil_to_native_quil_spy = mocker.spy(qc.compiler, "quil_to_native_quil")

    make_job(backend, circuit, qc)

    program: Program = quil_to_native_quil_spy.call_args[0][0]
    qasm = program.out(calibrations=False)
    assert qasm.startswith(
        'OPENQASM 2.0;\n#pragma INITIAL_REWIRING "NAIVE"'
    ), "circuit does not contain rewiring directive"


def test_init__circuit_with_active_reset(backend: RigettiQCSBackend, mocker: MockerFixture):
    circuit = make_circuit(backend.configuration().num_qubits)
    circuit.set_active_reset()
    qc = get_qc(backend.configuration().backend_name)
    compiler_native_quil_to_executable_spy = mocker.spy(qc.compiler, "native_quil_to_executable")

    make_job(backend, circuit, qc)

    program: Program = compiler_native_quil_to_executable_spy.call_args[0][0]
    quil = program.out(calibrations=False)
    assert quil.startswith("RESET\n"), "circuit does not start with RESET"


def test_result(job: RigettiQCSJob):
    result = job.result()

    assert result.date == job.result().date, "Result not cached"

    assert job.status() == JobStatus.DONE

    assert result.backend_name == "2q-qvm"
    assert result.job_id == job.job_id()
    assert result.success is True

    result_0 = result.results[0]
    assert result_0.success is True
    assert result_0.status == "Completed successfully"
    assert result_0.shots == 1000
    assert len(result_0.data.memory) == 1000

    # Note: this can flake if number of shots is not large enough -- 1000 should be enough
    assert result_0.data.counts.keys() == {"00", "01"}


def test_cancel(job: RigettiQCSJob):
    with pytest.raises(NotImplementedError, match="Cancelling jobs is not supported"):
        job.cancel()


def test_submit(job: RigettiQCSJob):
    with pytest.raises(
        NotImplementedError,
        match="'submit' is not implemented as this class uses the asynchronous pattern",
    ):
        job.submit()


@pytest.fixture
def backend():
    return RigettiQCSProvider().get_simulator(num_qubits=2)


@pytest.fixture
def job(backend):
    circuit = make_circuit(backend.configuration().num_qubits)
    return make_job(backend, circuit)


def make_circuit(num_qubits) -> QuilCircuit:
    circuit = QuilCircuit(QuantumRegister(num_qubits, "q"), ClassicalRegister(num_qubits, "ro"))
    circuit.h(0)
    circuit.measure(range(num_qubits), range(num_qubits))
    return circuit


def make_job(backend, circuit, qc: Optional[QuantumComputer] = None):
    qc = qc or get_qc(backend.configuration().backend_name)
    job = RigettiQCSJob(
        job_id="some_job",
        circuits=[circuit],
        options={"shots": 1000},
        qc=qc,
        backend=backend,
        configuration=backend.configuration(),
    )

    return job
