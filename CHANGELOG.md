# Changelog

## [0.4.3](https://github.com/rigetti/qiskit-rigetti/releases/tag/v0.4.3)

### New

- Added binder tutorials image


## [0.4.2](https://github.com/rigetti/qiskit-rigetti/releases/tag/v0.4.2)

### Updates

- Removed barrier support until quilc has better compatibility. For now, barriers are omitted during compilation from OpenQASM to Quil, though they will remain in effect for Qiskit's own transpilation/optimization passes (#15)

### Fixes

- Fix errors due to unbound circuits when calling `execute()` with parametric circuits and `parameter_binds` (#16)


## [0.4.1](https://github.com/rigetti/qiskit-rigetti/releases/tag/v0.4.1)

### Updates

- Limited support for barriers (#12)
- Added example notebooks to docs (#13)


## [0.4.0](https://github.com/rigetti/qiskit-rigetti/releases/tag/v0.4.0)

### Announcements

- Initial public release
