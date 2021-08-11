[![Tests](https://github.com/rigetti/qiskit-rigetti/actions/workflows/test.yml/badge.svg)](https://github.com/rigetti/qiskit-rigetti/actions/workflows/test.yml)
[![Documentation Status](https://readthedocs.org/projects/qiskit-rigetti/badge/?version=latest)](https://qiskit-rigetti.readthedocs.io/en/latest/?badge=latest)
[![pypi](https://img.shields.io/pypi/v/qiskit-rigetti.svg)](https://pypi.org/project/qiskit-rigetti/)
[![Binder](https://mybinder.org/badge_logo.svg)][binder]

# Rigetti Provider for Qiskit

## Try It Out

To try out this library, you can run example notebooks in a pre-made [binder][binder]. Alternately, you can run the following to build and run the image locally:

```bash
docker build -t qiskit-tutorials .
docker run --rm -p 8888:8888 qiskit-tutorials
```

then click on the link that is displayed after the container starts up.

[binder]: https://mybinder.org/v2/gh/rigetti/qiskit-rigetti/main?filepath=examples

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
from qiskit_rigetti import RigettiQCSProvider, QuilCircuit

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

### Rigetti Quantum Cloud Services (QCS)

Execution against a QPU requires a [reservation via QCS](https://docs.rigetti.com/qcs/guides/reserving-time-on-a-qpu).
For more information on using QCS, see the [QCS documentation](https://docs.rigetti.com).

## Advanced

### Lifecycle Hooks

For advanced QASM and Quil manipulation, `before_compile` and `before_execute` keyword arguments can be passed to
`RigettiQCSBackend.run()` or to Qiskit's `execute()`.

#### Pre-compilation Hooks

Any `before_compile` hooks will apply, in order, just before compilation from QASM to native Quil.
For example:

```python
...

def custom_hook_1(qasm: str) -> str:
   new_qasm = ...
   return new_qasm

def custom_hook_2(qasm: str) -> str:
   new_qasm = ...
   return new_qasm

job = execute(circuit, backend, shots=10, before_compile=[custom_hook_1, custom_hook_2])

...
```

#### Pre-execution Hooks

Any `before_execute` hooks will apply, in order, just before execution (after translation from QASM to native Quil).
For example:

```python
from pyquil import Program

...

def custom_hook_1(quil: Program) -> Program:
   new_quil = ...
   return new_quil

def custom_hook_2(quil: Program) -> Program:
   new_quil = ...
   return new_quil

job = execute(circuit, backend, shots=10, before_execute=[custom_hook_1, custom_hook_2])

...
```

> **Note**:
> 
> Only [certain forms of Quil can can be executed on a QPU](https://pyquil-docs.rigetti.com/en/stable/compiler.html?highlight=protoquil#legal-compiler-input).
> If pre-execution transformations produce a final program that is not QPU-compliant, `ensure_native_quil=True` can be
> passed to `execute()` or `RigettiQCSBackend.run()` to recompile the final Quil program to native Quil prior to
> execution. If no pre-execution hooks were supplied, this setting is ignored. If this setting is omitted, a value of
> `False` is assumed.
> 
> _Example_: Adding the Quil instruction `H 0` would result in an error if `ensure_native_quil=False` and the QPU does
> not natively implement Hadamard gates.

#### Built-in Hooks

The `hooks.pre_compilation` and `hooks.pre_execution` packages provide a number of convenient hooks:

##### `set_rewiring`

Use `set_rewiring` to provide a [rewiring directive](https://pyquil-docs.rigetti.com/en/stable/compiler.html#initial-rewiring)
to the Quil compiler. For example:

```python
from qiskit_rigetti.hooks.pre_compilation import set_rewiring

...

job = execute(circuit, backend, shots=10, before_compile=[set_rewiring("NAIVE")])

...
```

> **Note**: Rewiring directives require `quilc` version 1.25 or higher.

##### `enable_active_reset`

Use `enable_active_reset` to enable [active qubit reset](https://github.com/quil-lang/quil/blob/master/spec/Quil.md#state-reset),
an optimization that can significantly reduce the time between executions. For example:

```python
from qiskit_rigetti.hooks.pre_execution import enable_active_reset

...

job = execute(circuit, backend, shots=10, before_execute=[enable_active_reset])

...
```

## Development

> **Note**: This module is developed in Python 3.7, other versions will currently fail type checking.

Dependencies are managed with [Poetry](https://python-poetry.org/) so you need to install that first. Once you've installed all dependencies (`poetry install`) and activated the virtual environment (`poetry shell`), you can use these rules from the `Makefile` to run common tasks:

1. Run tests: `make test`
1. Check style and types: `make check-all`
1. Check style only: `make check-style`
1. Check types only: `make check-types`
1. Reformat all code (to make `check-style` pass): `make format`
1. Build documentation, serve locally, and watch for changes: `make watch-docs` (requires `docs` extra: `poetry install -E docs`)
