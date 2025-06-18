.PHONY: check lint typecheck test

# Runs linting, type-checking, and tests in one go
check: lint typecheck test

# Lint target (example)
lint:
	black --check .
	flake8 .

# Type-check target (example)
typecheck:
	mypy .

# Test target (example)
test:
	pytest --maxfail=1 --disable-warnings -q
