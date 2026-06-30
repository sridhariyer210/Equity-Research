.PHONY: fetch parse push refresh test lint format

fetch:
	python scripts/run_monthly.py --step fetch

parse:
	python scripts/run_monthly.py --step parse

push:
	python scripts/run_monthly.py --step push

refresh:
	python scripts/run_monthly.py --step all

test:
	pytest tests/ -v --cov=src

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/
