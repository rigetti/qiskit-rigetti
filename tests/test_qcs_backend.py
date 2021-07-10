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
import pytest
from pytest_mock import MockerFixture
from qiskit import execute, QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.providers import JobStatus

from qiskit_rigetti_provider import RigettiQCSProvider, RigettiQCSBackend, RigettiQCSJob


def test_run(backend: RigettiQCSBackend):
    circuit = make_circuit()

    job = execute(circuit, backend, shots=10)

    assert job.backend() is backend
    assert job.status() == JobStatus.RUNNING
    result = job.result()
    assert job.status() == JobStatus.DONE
    assert result.backend_name == backend.configuration().backend_name
    assert result.results[0].header.name == circuit.name
    assert result.results[0].shots == 10
    assert result.get_counts().keys() == {"00"}


def test_run__multiple_circuits(backend: RigettiQCSBackend):
    circuit1 = make_circuit(num_qubits=2)
    circuit2 = make_circuit(num_qubits=3)

    job = execute([circuit1, circuit2], backend, shots=10)

    assert job.backend() is backend
    result = job.result()
    assert job.status() == JobStatus.DONE

    assert result.backend_name == backend.configuration().backend_name
    assert len(result.results) == 2

    assert result.results[0].header.name == circuit1.name
    assert result.results[0].shots == 10
    assert result.get_counts(0).keys() == {"00"}

    assert result.results[1].header.name == circuit2.name
    assert result.results[1].shots == 10
    assert result.get_counts(1).keys() == {"000"}


def test_run__barrier(backend: RigettiQCSBackend):
    circuit = make_circuit()
    circuit.barrier()
    qasm_before = circuit.qasm()

    with pytest.warns(UserWarning, match="`barrier` has no effect on a RigettiQCSBackend and will be omitted"):
        job = execute(circuit, backend, shots=10)

    assert circuit.qasm() == qasm_before, "should not modify original circuit"

    assert job.backend() is backend
    result = job.result()
    assert job.status() == JobStatus.DONE
    assert result.backend_name == backend.configuration().backend_name
    assert result.results[0].header.name == circuit.name
    assert result.results[0].shots == 10
    assert result.get_counts().keys() == {"00"}


def test_run__multiple_readout_registers(backend: RigettiQCSBackend):
    qr = QuantumRegister(2, "q")
    cr = ClassicalRegister(1, "c")
    cr2 = ClassicalRegister(1, "c2")
    circuit = QuantumCircuit(qr, cr, cr2)
    circuit.measure([qr[0], qr[1]], [cr[0], cr2[0]])

    with pytest.raises(RuntimeError, match="Multiple readout registers are unsupported on QCSBackend; found c, c2"):
        execute(circuit, backend, shots=10)


def test_run__readout_register_not_named_ro(backend: RigettiQCSBackend):
    circuit = make_circuit(readout_name="not_ro")
    qasm_before = circuit.qasm()

    job = execute(circuit, backend, shots=10)

    assert circuit.qasm() == qasm_before, "should not modify original circuit"

    assert job.backend() is backend
    result = job.result()
    assert job.status() == JobStatus.DONE
    assert result.backend_name == backend.configuration().backend_name
    assert result.results[0].header.name == circuit.name
    assert result.results[0].shots == 10
    assert result.get_counts().keys() == {"00"}


def test_run__pre_compilation_hook(backend: RigettiQCSBackend, mocker: MockerFixture):
    circuit = make_circuit()

    def pre_compilation_hook(qasm: str) -> str:
        return qasm

    job_init_spy = mocker.spy(RigettiQCSJob, "__init__")
    job = execute(circuit, backend, shots=10, before_compile=pre_compilation_hook)
    result = job.result()

    assert result.get_counts().keys() == {"00"}
    assert job_init_spy.call_args[1]["before_compile"] == [pre_compilation_hook]


def test_run__pre_compilation_hook__multiple(backend: RigettiQCSBackend, mocker: MockerFixture):
    circuit = make_circuit()

    def pre_compilation_hook_1(qasm: str) -> str:
        return qasm

    def pre_compilation_hook_2(qasm: str) -> str:
        return qasm

    job_init_spy = mocker.spy(RigettiQCSJob, "__init__")
    job = execute(circuit, backend, shots=10, before_compile=[pre_compilation_hook_1, pre_compilation_hook_2])
    result = job.result()

    assert result.get_counts().keys() == {"00"}
    assert job_init_spy.call_args[1]["before_compile"] == [pre_compilation_hook_1, pre_compilation_hook_2]


def test_run__pre_compilation_hook__missing(backend: RigettiQCSBackend, mocker: MockerFixture):
    circuit = make_circuit()

    job_init_spy = mocker.spy(RigettiQCSJob, "__init__")
    job = execute(circuit, backend, shots=10)
    result = job.result()

    assert result.get_counts().keys() == {"00"}
    assert job_init_spy.call_args[1]["before_compile"] == []


def test_run__pre_execution_hook(backend: RigettiQCSBackend, mocker: MockerFixture):
    circuit = make_circuit()

    def pre_execution_hook(qasm: str) -> str:
        return qasm

    job_init_spy = mocker.spy(RigettiQCSJob, "__init__")
    job = execute(circuit, backend, shots=10, before_execute=pre_execution_hook)
    result = job.result()

    assert result.get_counts().keys() == {"00"}
    assert job_init_spy.call_args[1]["before_execute"] == [pre_execution_hook]


def test_run__pre_execution_hook__multiple(backend: RigettiQCSBackend, mocker: MockerFixture):
    circuit = make_circuit()

    def pre_execution_hook_1(qasm: str) -> str:
        return qasm

    def pre_execution_hook_2(qasm: str) -> str:
        return qasm

    job_init_spy = mocker.spy(RigettiQCSJob, "__init__")
    job = execute(circuit, backend, shots=10, before_execute=[pre_execution_hook_1, pre_execution_hook_2])
    result = job.result()

    assert result.get_counts().keys() == {"00"}
    assert job_init_spy.call_args[1]["before_execute"] == [pre_execution_hook_1, pre_execution_hook_2]


def test_run__pre_execution_hook__missing(backend: RigettiQCSBackend, mocker: MockerFixture):
    circuit = make_circuit()

    job_init_spy = mocker.spy(RigettiQCSJob, "__init__")
    job = execute(circuit, backend, shots=10)
    result = job.result()

    assert result.get_counts().keys() == {"00"}
    assert job_init_spy.call_args[1]["before_execute"] == []


def test_run__ensure_native_quil(backend: RigettiQCSBackend, mocker: MockerFixture):
    circuit = make_circuit()

    job_init_spy = mocker.spy(RigettiQCSJob, "__init__")
    job = execute(circuit, backend, shots=10, ensure_native_quil=True)
    result = job.result()

    assert result.get_counts().keys() == {"00"}
    assert job_init_spy.call_args[1]["ensure_native_quil"] is True


def test_run__ensure_native_quil__missing(backend: RigettiQCSBackend, mocker: MockerFixture):
    circuit = make_circuit()

    job_init_spy = mocker.spy(RigettiQCSJob, "__init__")
    job = execute(circuit, backend, shots=10)
    result = job.result()

    assert result.get_counts().keys() == {"00"}
    assert job_init_spy.call_args[1]["ensure_native_quil"] is False


@pytest.fixture
def backend():
    return RigettiQCSProvider().get_simulator(num_qubits=3)


def make_circuit(*, num_qubits: int = 2, readout_name: str = "ro"):
    circuit = QuantumCircuit(QuantumRegister(num_qubits, "q"), ClassicalRegister(num_qubits, readout_name))
    circuit.measure(list(range(num_qubits)), list(range(num_qubits)))
    return circuit
