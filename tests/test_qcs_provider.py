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
import os

from qcs_sdk.qpu.isa import InstructionSetArchitecture
from qiskit_rigetti import RigettiQCSProvider


def test_get_simulator(monkeypatch):
    backend = RigettiQCSProvider().get_simulator(num_qubits=42)

    assert backend.name() == "42q-qvm"
    assert backend.configuration().num_qubits == 42
    # The default QVM url is 127.0.0.1, but Gitlab CI may use a docker service url.
    # Below we assert that the local value on the configuration is True/False depending
    # on the `QCS_SETTINGS_APPLICATIONS_QVM_URL` set during the test run.
    assert (
        "http://qvm:5000" != os.getenv("QCS_SETTINGS_APPLICATIONS_QVM_URL", "http://127.0.0.1:5000")
    ) == backend.configuration().local
    assert backend.configuration().simulator
    assert backend.configuration().coupling_map


def test_get_simulator__noisy(monkeypatch):
    backend = RigettiQCSProvider().get_simulator(num_qubits=42, noisy=True)

    assert backend.name() == "42q-noisy-qvm"
    assert backend.configuration().num_qubits == 42
    assert ("qvm:" not in os.getenv("QCS_SETTINGS_APPLICATIONS_QVM_URL", "")) == backend.configuration().local
    assert backend.configuration().simulator
    assert backend.configuration().coupling_map


def test_run__backend_coupling_map():
    backend = RigettiQCSProvider().get_simulator(num_qubits=3)
    assert backend.configuration().coupling_map
    assert [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)] == sorted(backend.configuration().coupling_map)


@pytest.mark.parametrize(
    "qvm_url",
    [
        "http://example.com/qvm",
        "http://localhost:9999/qvm",
        "http://127.0.0.1:9999/qvm",
    ],
)
def test_get_simulator__remote(qvm_url: str, monkeypatch):
    monkeypatch.setenv("QCS_SETTINGS_APPLICATIONS_QVM_URL", qvm_url)

    with pytest.raises(Exception, match="failed to retrieve quantum processor"):
        _ = RigettiQCSProvider().get_simulator(num_qubits=42)


def test_backends():
    def simple_isa(nodes: int):
        from json import dumps

        return InstructionSetArchitecture.from_raw(
            dumps(
                {
                    "architecture": {
                        "nodes": [{"node_id": i} for i in range(nodes)],
                        "edges": [],
                    },
                    "benchmarks": [],
                    "instructions": [],
                    "name": "_",
                }
            )
        )

    provider = RigettiQCSProvider()
    provider._get_quantum_processors = lambda: {
        "Device-1": simple_isa(1),
        "Device-2": simple_isa(2),
    }
    backends = provider.backends()

    assert len(backends) == 2

    backend1 = provider.backends("Device-1")[0]
    assert backend1.configuration().num_qubits == 1
    assert backend1.configuration().local is False
    assert backend1.configuration().simulator is False

    backend2 = provider.backends("Device-2")[0]
    assert backend2.configuration().num_qubits == 2
    assert backend2.configuration().local is False
    assert backend2.configuration().simulator is False
