.PHONY: install test test-cov lint format serve clean

install:
	pip install -r requirements.txt
	pip install -e ".[dev]"

test:
	pytest

test-cov:
	pytest --cov=internal --cov=api --cov=cmd --cov-report=term-missing --cov-report=html

lint:
	ruff check .
	mypy internal api cmd

format:
	black .
	ruff check --fix .

serve:
	python -m cmd.shomer serve

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

