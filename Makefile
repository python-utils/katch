#!make

VERSION ?= $(shell git describe --tags --exact-match || git rev-parse --abbrev-ref HEAD)

ROOT_PY3 := python3
VENV ?= venv
BIN=$(VENV)/bin
PIP := $(BIN)/pip
PYTHON := $(BIN)/python
PYTHON_SETUP := python setup.py
PYTEST := pytest
LIBDIR ?= katch/
BANDIT := bandit
SAFETY := safety
BLACK := black

.PHONY: venv setup ci-setup test-verbose test-cov test-cov-html test \
		check-style check-security check-dependencies ci

venv:
	$(ROOT_PY3) -m virtualenv $(VENV)

setup:
	$(PIP) install -e .

ci-setup:
	$(PIP) install -e .[test]

test-verbose: PYTEST_ARGS += --verbose
test-verbose: test

test-cov: PYTEST_ARGS += --cov=$(LIBDIR)
test-cov: test

test-cov-html: PYTEST_ARGS += --cov=$(LIBDIR) --cov-report html
test-cov-html: test

test:
	$(PYTHON) -m $(PYTEST) $(PYTEST_ARGS)

check-style:
	$(PYTHON) -m $(BLACK) --check $(LIBDIR)

check-security:
	$(PYTHON) -m $(BANDIT) --r $(LIBDIR)

check-dependencies: ci-setup
	$(PYTHON) -m $(SAFETY) check

ci: ci-setup check-style check-security check-dependencies test-cov
