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
from qcs_api_client.util.errors import QCSHTTPStatusError
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, execute
from qiskit.circuit import Parameter
from qiskit.providers import JobStatus
from qiskit_rigetti import RigettiQCSBackend, RigettiQCSProvider


def test_run(backend: RigettiQCSBackend):
    circuit = make_circuit()

    job = execute(circuit, backend, shots=10)

    assert job.backend() is backend
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


def test_run__parametric_circuits(backend: RigettiQCSBackend):
    t = Parameter("t")

    circuit1 = QuantumCircuit(QuantumRegister(1, "q"), ClassicalRegister(1, "ro"))
    circuit1.rx(t, 0)
    circuit1.measure([0], [0])

    circuit2 = QuantumCircuit(QuantumRegister(1, "q"), ClassicalRegister(1, "ro"))
    circuit2.ry(t, 0)
    circuit2.measure([0], [0])

    job = execute(
        [circuit1, circuit2],
        backend,
        shots=1000,
        parameter_binds=[
            {t: 1.0},
            {t: 2.0},
        ],
    )

    assert job.backend() is backend
    result = job.result()
    assert job.status() == JobStatus.DONE

    assert result.backend_name == backend.configuration().backend_name
    assert len(result.results) == 4

    assert result.results[0].header.name.startswith(f"{circuit1.name}-")
    assert result.results[0].shots == 1000
    assert result.get_counts(0).keys() == {"0", "1"}

    assert result.results[1].header.name.startswith(f"{circuit1.name}-")
    assert result.results[1].shots == 1000
    assert result.get_counts(1).keys() == {"0", "1"}

    assert result.results[2].header.name.startswith(f"{circuit2.name}-")
    assert result.results[2].shots == 1000
    assert result.get_counts(2).keys() == {"0", "1"}

    assert result.results[3].header.name.startswith(f"{circuit2.name}-")
    assert result.results[3].shots == 1000
    assert result.get_counts(3).keys() == {"0", "1"}


def test_run__readout_register_not_named_ro(backend: RigettiQCSBackend):
    circuit = QuantumCircuit(QuantumRegister(2, "q"), ClassicalRegister(2, "not_ro"))
    circuit.measure([0, 1], [0, 1])
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


def test_run__multiple_registers__single_readout(backend: RigettiQCSBackend):
    readout_reg = ClassicalRegister(2, "not_ro")
    circuit = QuantumCircuit(QuantumRegister(2, "q"), ClassicalRegister(2, "c"), readout_reg)
    circuit.measure([0, 1], [readout_reg[0], readout_reg[1]])
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


def test_run__multiple_readout_registers(backend: RigettiQCSBackend):
    qr = QuantumRegister(2, "q")
    cr = ClassicalRegister(1, "c")
    cr2 = ClassicalRegister(1, "c2")
    circuit = QuantumCircuit(qr, cr, cr2)
    circuit.measure([qr[0], qr[1]], [cr[0], cr2[0]])

    with pytest.raises(RuntimeError, match="Multiple readout registers are unsupported on QCSBackend; found c, c2"):
        execute(circuit, backend, shots=10)


def test_run__no_measurments(backend: RigettiQCSBackend):
    qr = QuantumRegister(2, "q")
    cr = ClassicalRegister(1, "c")
    circuit = QuantumCircuit(qr, cr)

    with pytest.raises(RuntimeError, match="Circuit has no measurements"):
        execute(circuit, backend, shots=10)


def test_error_is_raised_if_neither_backend_name_or_qubits_specified(monkeypatch):
    monkeypatch.delenv("QCS_SETTINGS_APPLICATIONS_PYQUIL_QVM_URL", raising=False)

    backend = RigettiQCSProvider().get_simulator()
    with pytest.raises(QCSHTTPStatusError):
        backend.run(make_circuit(num_qubits=1))


def test_error_is_raised_if_backend_simulator_name_doesnt_exist(monkeypatch):
    monkeypatch.delenv("QCS_SETTINGS_APPLICATIONS_PYQUIL_QVM_URL", raising=False)

    backend = RigettiQCSProvider().get_simulator(name="non-existent")
    with pytest.raises(QCSHTTPStatusError):
        backend.run(make_circuit(num_qubits=1))


@pytest.fixture
def backend():
    return RigettiQCSProvider().get_simulator(num_qubits=3)


def make_circuit(*, num_qubits: int = 2):
    circuit = QuantumCircuit(QuantumRegister(num_qubits, "q"), ClassicalRegister(num_qubits, "ro"))
    circuit.measure(list(range(num_qubits)), list(range(num_qubits)))
    return circuit
