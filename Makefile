.PHONY: help install dev test lint format clean verify check

# Default target
help:
	@echo "Peircean Abduction - Development Tasks"
	@echo "======================================"
	@echo "make install    : Install dependencies"
	@echo "make dev        : Install development dependencies"
	@echo "make test       : Run tests"
	@echo "make lint       : Run static analysis (Ruff, MyPy)"
	@echo "make format     : Auto-format code (Ruff)"
	@echo "make verify     : Run MCP verification script"
	@echo "make clean      : Clean build artifacts"
	@echo "make check      : Run all checks (format, lint, test, verify)"

install:
	pip install -e .

dev:
	pip install -e ".[dev,all]"
	pre-commit install

test:
	pytest

lint:
	ruff check .
	mypy .

format:
	ruff format .
	ruff check --fix .

verify:
	python scripts/validate_mcp.py

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '.pytest_cache' -exec rm -rf {} +
	find . -name '.ruff_cache' -exec rm -rf {} +
	find . -name '.mypy_cache' -exec rm -rf {} +
	find . -name '.coverage' -exec rm -f {} +

check: format lint test verify
