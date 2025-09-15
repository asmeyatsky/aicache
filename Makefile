VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python

.PHONY: install install-wrappers setup test clean

venv:
	test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)

install:
	$(PYTHON) -m pip install .

install-wrappers:
	mkdir -p ~/.local/bin
	cp $(VENV_DIR)/bin/aicache ~/.local/bin/gcloud
	cp $(VENV_DIR)/bin/aicache ~/.local/bin/llm
	cp $(VENV_DIR)/bin/aicache ~/.local/bin/openai
	cp custom_wrappers/claude ~/.local/bin/claude
	cp custom_wrappers/gemini ~/.local/bin/gemini
	cp custom_wrappers/qwen ~/.local/bin/qwen
	chmod +x ~/.local/bin/claude ~/.local/bin/gemini ~/.local/bin/qwen
	@echo "Wrapper scripts installed in ~/.local/bin"
	@echo "Please ensure ~/.local/bin is in your PATH and has precedence."

setup: install install-wrappers

test: venv
	$(PYTHON) -m pip install -e .
	$(PYTHON) -m pip install pytest-asyncio
	$(PYTHON) -m pytest tests/test_core.py tests/test_cli_wrappers.py -v

clean:
	rm -rf build dist *.egg-info .aicache .pytest_cache test_project test_project_cli $(VENV_DIR)