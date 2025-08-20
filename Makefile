VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python

.PHONY: install install-wrappers setup test clean

venv:
	test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)

install:
	$(PYTHON) -m pip install .

install-wrappers:
	mkdir -p ~/.local/bin
	cp scripts/gcloud_wrapper.py ~/.local/bin/gcloud
	cp scripts/llm_wrapper.py ~/.local/bin/llm
	@echo "Wrapper scripts installed in ~/.local/bin"
	@echo "Please ensure ~/.local/bin is in your PATH and has precedence."

setup: install install-wrappers

test: venv
	$(PYTHON) -m pip install -e .
	$(PYTHON) -m unittest discover -s tests

clean:
	rm -rf build dist *.egg-info .aicache .pytest_cache test_project test_project_cli $(VENV_DIR)
