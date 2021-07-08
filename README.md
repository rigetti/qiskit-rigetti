[![Tests](https://github.com/rigetti/qiskit-rigetti-provider/actions/workflows/test.yml/badge.svg)](https://github.com/rigetti/qiskit-rigetti-provider/actions/workflows/test.yml)

# Qiskit Rigetti Provider

## Pre-requisites

1. Install [Docker](https://www.docker.com/products/docker-desktop)
1. Download [qelib1.inc](https://raw.githubusercontent.com/Qiskit/qiskit-terra/0.16.2/qiskit/qasm/libs/qelib1.inc)
1. Place `qelib1.inc` in a folder called `inc` in the project root

## Setup QVM and quilc

> **NOTE:**
> 
> For rewiring pragma support (i.e. `QuilCircuit.set_rewiring()`), ensure the quilc version is at least v1.25.

### Using Docker Compose

Run `docker compose up` to see service logs or `docker compose up -d` to run in the background.

### Using Docker Manually

1. Start the QVM:
   
   ```bash
   docker run --rm -it -p 5000:5000 rigetti/qvm -S
   ```

1. Start the compiler:

   ```bash
   docker run --rm -it -p 5555:5555 -v "$PWD"/inc:/inc rigetti/quilc -S -P --safe-include-directory /inc/
   ```

## Usage

Example:

```python
from qiskit import execute
from qiskit_rigetti_provider import RigettiQCSProvider, QuilCircuit

# Get provider and backend
p = RigettiQCSProvider()
backend = p.get_simulator(num_qubits=2, noisy=True)  # or p.get_backend(name='Aspen-9')

# Create a Bell state circuit
circuit = QuilCircuit(2, 2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure([0, 1], [0, 1])

# Execute the circuit on the backend
job = execute(circuit, backend, shots=10)

# Grab results from the job
result = job.result()

# Return memory and counts
memory = result.get_memory(circuit)
counts = result.get_counts(circuit)
print("Result memory:", memory)
print("Result counts:", counts)
```

## Development

To run tests:

```bash
make test
```

To run style and type checks:

```bash
make check-all
```

> Use the `check-style` or `check-types` Make tasks to run style and type checks individually.

You can reformat all code according to this project's style configuration with:

```bash
make format
```
