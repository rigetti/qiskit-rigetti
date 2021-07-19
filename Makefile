PACKAGE_NAME = qiskit_rigetti

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
	pytest -v --cov=$(PACKAGE_NAME) --cov-report=term --doctest-modules tests qiskit_rigetti

.PHONY: docs
docs:
	$(MAKE) -C docs html

.PHONY: watch-docs
watch-docs:
	sphinx-autobuild docs docs/_build/html
