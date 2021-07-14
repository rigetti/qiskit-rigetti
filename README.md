[![Tests](https://github.com/rigetti/qiskit-rigetti-provider/actions/workflows/test.yml/badge.svg)](https://github.com/rigetti/qiskit-rigetti-provider/actions/workflows/test.yml)

# Qiskit Rigetti Provider

## Pre-requisites

1. Install [Docker](https://www.docker.com/products/docker-desktop)
1. Download [qelib1.inc](https://raw.githubusercontent.com/Qiskit/qiskit-terra/0.16.2/qiskit/qasm/libs/qelib1.inc)
1. Place `qelib1.inc` in a folder called `inc` in the project root

## Setup QVM and quilc

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

## Advanced

### Lifecycle Hooks

For more advanced QASM and Quil modification, pass a `before_compile` or `before_execute` function as a keyword argument to
`RigettiQCSBackend.run()` or to Qiskit's `execute()`.

#### Pre-compilation Hooks

The `before_compile` hook will apply just before compilation from QASM to native Quil.
For example:

```python
...

def custom_hook(qasm: str) -> str:
   new_qasm = ...
   return new_qasm

job = execute(circuit, backend, shots=10, before_compile=custom_hook)

...
```

#### Pre-execution Hooks

The `before_execute` hook will apply just before execution (after translation from QASM to native Quil).
For example:

```python
from pyquil import Program

...

def custom_hook(quil: Program) -> Program:
   new_quil = ...
   return new_quil

job = execute(circuit, backend, shots=10, before_execute=custom_hook)

...
```

#### Built-in Hooks

The `hooks.pre_compilation` and `hooks.pre_execution` packages provide a number of convenient hooks:

##### `set_rewiring`

Use `set_rewiring` to provide a [rewiring directive](https://pyquil-docs.rigetti.com/en/stable/compiler.html#initial-rewiring)
to the Quil compiler. For example:

```python
from qiskit_rigetti_provider.hooks.pre_compilation import set_rewiring

...

job = execute(circuit, backend, shots=10, before_compile=set_rewiring("NAIVE"))

...
```

> **Note**: Rewiring directives require `quilc` version 1.25 or higher.

##### `enable_active_reset`

Use `enable_active_reset` to enable [active qubit reset](https://github.com/quil-lang/quil/blob/master/spec/Quil.md#state-reset),
an optimization that can speed up multi-shot execution. For example:

```python
from qiskit_rigetti_provider.hooks.pre_execution import enable_active_reset

...

job = execute(circuit, backend, shots=10, before_execute=enable_active_reset)

...
```

#### Multiple Hooks

To use multiple hooks, simply supply a sequence of hooks for either `before_compile` or `before_execute`, and the
provided hooks will be executed in order. For example:

```python
from qiskit_rigetti_provider.hooks.pre_execution import enable_active_reset

...

def custom_hook(quil: Program) -> Program:
   new_quil = ...
   return new_quil

job = execute(circuit, backend, shots=10, before_execute=[enable_active_reset, custom_hook])

...
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
