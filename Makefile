# top-level Makefile

SRC := .

.PHONY: check lint typecheck test

# Runs linting, type-checking, and tests in one go
check: lint typecheck test

# Lint target: only your source dirs, Flake8 in parallel
lint:
	black --check $(SRC)
	flake8 --jobs=auto $(SRC)

# Type-check target
typecheck:
	mypy $(SRC) \
	  --ignore-missing-imports \
	  --install-types \
	  --non-interactive \
	  --exclude 'venv/|\.venv/|build/|dist/|node_modules/'
# Test target
test:
	pytest --maxfail=1 --disable-warnings -q
format:
	black $(SRC)

coverage:
	pytest --maxfail=1 --disable-warnings --cov=$(SRC) --cov-report=term-missing -q