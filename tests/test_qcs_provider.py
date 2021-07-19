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
from pytest_httpx import HTTPXMock

from qiskit_rigetti import RigettiQCSProvider


def test_get_simulator(monkeypatch):
    monkeypatch.delenv("QCS_SETTINGS_APPLICATIONS_PYQUIL_QVM_URL", raising=False)

    backend = RigettiQCSProvider().get_simulator(num_qubits=42)

    assert backend.name() == "42q-qvm"
    assert backend.configuration().num_qubits == 42
    assert backend.configuration().local is True
    assert backend.configuration().simulator is True


def test_get_simulator__noisy(monkeypatch):
    monkeypatch.delenv("QCS_SETTINGS_APPLICATIONS_PYQUIL_QVM_URL", raising=False)

    backend = RigettiQCSProvider().get_simulator(num_qubits=42, noisy=True)

    assert backend.name() == "42q-noisy-qvm"
    assert backend.configuration().num_qubits == 42
    assert backend.configuration().local is True
    assert backend.configuration().simulator is True


def test_get_simulator__remote(monkeypatch):
    monkeypatch.setenv("QCS_SETTINGS_APPLICATIONS_PYQUIL_QVM_URL", "http://example.com/qvm")

    backend = RigettiQCSProvider().get_simulator(num_qubits=42)

    assert backend.name() == "42q-qvm"
    assert backend.configuration().num_qubits == 42
    assert backend.configuration().local is False
    assert backend.configuration().simulator is True


def test_get_simulator__localhost(monkeypatch):
    monkeypatch.setenv("QCS_SETTINGS_APPLICATIONS_PYQUIL_QVM_URL", "http://localhost:9999/qvm")

    backend = RigettiQCSProvider().get_simulator(num_qubits=42)

    assert backend.name() == "42q-qvm"
    assert backend.configuration().num_qubits == 42
    assert backend.configuration().local is True
    assert backend.configuration().simulator is True


def test_get_simulator__local_ip(monkeypatch):
    monkeypatch.setenv("QCS_SETTINGS_APPLICATIONS_PYQUIL_QVM_URL", "http://127.0.0.1:9999/qvm")

    backend = RigettiQCSProvider().get_simulator(num_qubits=42)

    assert backend.name() == "42q-qvm"
    assert backend.configuration().num_qubits == 42
    assert backend.configuration().local is True
    assert backend.configuration().simulator is True


def test_backends(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://forest-server.qcs.rigetti.com/devices",
        json={
            "devices": {
                "Device-1": {
                    "num_qubits": 1,
                },
                "Device-2": {
                    "num_qubits": 2,
                },
            },
        },
    )

    provider = RigettiQCSProvider()
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
