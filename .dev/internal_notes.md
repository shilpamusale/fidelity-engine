# Task 1: Create & Initialize MedSentinel/

## 1. Create and move into project folder

``` bash
mkdir MedSentinel && cd MedSentinel
```
## 2. Initialize Git

``` bash
git init

```

## 3. Create Python virtual environment

``` bash
python3 -m venv .venv
source .venv/bin/activate  ## On Windows: .venv\Scripts\activate

```
## 4. Create initial folder structure

``` bash
mkdir medsentinel tests .github .github/workflows
touch medsentinel/__init__.py tests/test_sanity.py README.md

```
# Task 2: Install + Lock Tooling

## 5. Install Required Tools in Virtual Env

``` bash
pip install --upgrade pip
pip install black ruff mypy pytest pre-commit
```

## 6. Freeze and Lock Dependencies

``` bash
pip freeze > requirements.txt
cp requirements.txt requirements.lock.txt
```
## 7. Sanity Check

``` bash
black --version
ruff --version
mypy --version
pytest --version
pre-commit --version

```

# Task 3: Add Config Files

## 1. .pre-commit-config.yaml

```yaml
    repos:
    - repo: https://github.com/psf/black
        rev: 24.3.0
        hooks:
        - id: black

    - repo: https://github.com/charliermarsh/ruff-pre-commit
        rev: v0.4.0
        hooks:
        - id: ruff

    - repo: https://github.com/pre-commit/mirrors-mypy
        rev: v1.9.0
        hooks:
        - id: mypy
```

##  2. pyproject.toml (for black and ruff)

```toml:
    [tool.black]
    line-length = 88
    target-version = ["py310"]

    [tool.ruff]
    line-length = 88
    target-version = "py310"
    select = ["E", "F", "I", "N", "UP"]

```
##  3. mypy.ini

```bash:
    [mypy]
    python_version = 3.10
    strict = True
    ignore_missing_imports = True
    disallow_untyped_defs = True
    check_untyped_defs = True
    show_error_codes = True

```

##  4. pytest.ini

```bash:
[pytest]
addopts = -ra
testpaths = tests

```

# Task 4: Testing, Pre-Commit, and GitHub CI

## Step 1: Add Sanity Test

```python
def test_sanity():
    assert True
```

## Step 2: Initialize Pre-Commit

```bash
pre-commit install
pre-commit run --all-files

```

## 🚦 Step 3: Add GitHub Actions Workflow

### Create this file:

```bash
.github/workflows/ci.yml
```

With content:

```yaml
name: CI

on: [push, pull_request]

jobs:
  lint-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m venv .venv
          source .venv/bin/activate
          pip install -r requirements.txt

      - name: Run linters and tests
        run: |
          black --check .
          ruff .
          mypy medsentinel
          pytest
```

## 🚦 Step 4: Add a Makefile

```makefile
.PHONY: lint format test typecheck all check

lint:
	ruff medsentinel tests

format:
	black medsentinel tests

test:
	pytest

typecheck:
	mypy medsentinel

all: format lint typecheck test

check: lint typecheck test
```

### 🛠️ You Can Now Run:

| Command          | What It Does                       |
| ---------------- | ---------------------------------- |
| `make lint`      | Runs `ruff` on your code and tests |
| `make format`    | Runs `black` to auto-format code   |
| `make test`      | Runs `pytest`                      |
| `make typecheck` | Runs `mypy` static type checking   |
| `make check`     | Lint + typecheck + test            |
| `make all`       | Format + lint + typecheck + test   |

### 🧪 Optional: Add to CI Later

#### 1. You can replace this block in ci.yml:
``` yaml
        - name: Run linters and tests
        run: |
            black --check .
            ruff .
            mypy medsentinel
            pytest

with 
        - name: Run Makefile checks
          run: make check

```
- #### 🎯 Why Add Makefile to CI?
    - ✅ 1. Simplifies CI Scripts
        Instead of repeating long CLI commands in every ci.yml job:
        This:

            - Keeps your CI config clean

            - Ensures consistency between local dev and CI

            - Makes the pipeline easier to update (you only change the Makefile)
    - ✅ 2. Unifies Dev and CI Behavior . Using make check locally and in CI ensures you’re running the same lint/type/test stack in both places. No surprises on GitHub.

    - ✅ 3. FAANG-Style Dev Ergonomics
        At companies like Anthropic, LinkedIn, Netflix:

        Engineers use make test, make check, make dev-setup for daily workflows

        It becomes second nature: one command = many things done right

    - ✅ 4. Future-Proofing
        Later, if you add:

        Code coverage tools

        FastAPI server

        Streamlit dashboard

        Docs build with Sphinx or MkDocs

        …you can just define make serve, make docs, make cov, etc.

        CI stays simple — you just call the corresponding make targets.

    - ⚠️ When You Wouldn’t Add It to CI
        If your CI is already minimal and you don’t want the extra layer yet.

        Or if you’re in a team that prefers Bash scripts over Makefiles (some ML orgs do).

        Bottom Line:
    - ✅ Add it if you want clean CI, consistent dev workflows, and scalability.
        It’s optional, but it’s the FAANG way.


## Step 5: Add a .gitignore

``` bash
# Python virtualenv
.venv/
venv/
ENV/
env/

# Python bytecode
__pycache__/
*.py[cod]

# Jupyter Notebooks
.ipynb_checkpoints/

# Pytest cache
.pytest_cache/

# Mypy cache
.mypy_cache/

# Ruff cache
.ruff_cache/

# VSCode and other IDEs
.vscode/
.idea/

# OS files
.DS_Store

# Dependency lock
pip-log.txt

# Coverage reports (if added later)
htmlcov/
.coverage

# Compiled files
*.so


```

## Step 6: Commit + Push to GitHub

```bash
git add .
git commit -m "Day 0: Project scaffolding, tool setup, sanity test, and CI"
git remote add origin https://github.com/ishi3012/medsentinel.git
git push -u origin main
```

# ✅ MedSentinel Git + CI Preflight Commands
### 🔹 1. Make sure you're on the correct branch
```bash
git status
```
Check:

You’re on main or a feature branch (e.g., feat/day2-cot-skill)

There are no uncommitted changes unless intentional

### 🔹 2. Pull latest changes from GitHub
```bash
git pull --rebase
```
Prevents push conflicts and keeps your history clean

### 🔹 3. Run full quality gates (via Makefile)
```bash

make format      # Format with black
make lint        # Check code style with ruff
make typecheck   # Run mypy static type checks
make test        # Run all tests

# or if you’re confident:

make check       # Run all above except formatting
```
### 🔹 4. Run pre-commit manually (catches missed stuff)
```bash
pre-commit run --all-files
```
Useful if you haven’t committed yet or added new files

### 🔹 5. Stage and commit cleanly
```bash

git add .
git commit -m "feat: Add <module> with tests and CI pass"
```
### 🔹 6. Push to remote
```bash
git push origin <branch-name>
# If on main, use:
git push

#If on a feature branch:
git push -u origin feat/day2-cot-skill
```
## 🧠 Bonus: Clean Git Hygiene 
| Habit                                            | Command                  |
| ------------------------------------------------ | ------------------------ |
| Restore a deleted file you didn’t mean to remove | `git restore <file>`     |
| See what exactly changed before commit           | `git diff`               |
| Interactively stage only parts of a file         | `git add -p`             |
| Re-run CI locally if needed                      | `make check` or `pytest` |
| Check ignored files                              | `cat .gitignore`         |

