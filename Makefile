PACKAGE_NAME = qiskit_rigetti_provider

.PHONY: format
format:
	black .

.PHONY: check-all
check-all: check-types check-style

.PHONY: check-style
check-style:
	black --check --diff .
	flake8 $(PACKAGE_NAME)

.PHONY: check-types
check-types:
	mypy $(PACKAGE_NAME)

.PHONY: test
test:
	pytest -v --cov=$(PACKAGE_NAME) --cov-report=term tests
