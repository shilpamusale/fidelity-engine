.PHONY: lint format test typecheck all check

lint:
	ruff check medsentinel tests

format:
	black medsentinel tests

test:
	PYTHONPATH=$(PWD) pytest

typecheck:
	mypy medsentinel

all: format lint typecheck test

check: lint typecheck test
