.PHONY: install install-wrappers setup test clean

install:
	pip install .

install-wrappers:
	mkdir -p ~/.local/bin
	cp scripts/gcloud_wrapper.py ~/.local/bin/gcloud
	cp scripts/llm_wrapper.py ~/.local/bin/llm
	@echo "Wrapper scripts installed in ~/.local/bin"
	@echo "Please ensure ~/.local/bin is in your PATH and has precedence."

setup: install install-wrappers

test:
	python3 -m unittest discover -s tests

clean:
	rm -rf build dist *.egg-info .aicache .pytest_cache test_project
