SHELL=/bin/bash
VENV_DIR=venv
PYTHON=$(shell which python3)

ifeq ($(OS),Windows_NT)
VENV_BIN=$(VENV_DIR)/Scripts
else
VENV_BIN=$(VENV_DIR)/bin
endif

$(VENV_DIR): requirements.txt requirements-dev.txt
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_BIN)/python -m pip install --upgrade pip 'setuptools<82.0.0'
	$(VENV_BIN)/python -m pip install -r requirements.txt -r requirements-dev.txt

.PHONY: pre-commit
pre-commit: $(VENV_DIR)
	$(VENV_BIN)/pre-commit install -f --install-hooks
	$(VENV_BIN)/pre-commit run --all-files

.PHONY: test
test: pre-commit
	$(VENV_BIN)/mypy ./stats_server
	$(VENV_BIN)/check-requirements -v

.PHONY: clean
clean:
	rm -rf $(VENV_DIR) .mypy_cache .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} \;
