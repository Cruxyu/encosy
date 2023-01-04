.ONESHELL:
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")
USING_POETRY=$(shell grep "tool.poetry" pyproject.toml && echo "yes")

.EXPORT_ALL_VARIABLES:
TAG = $(shell cat encosy/VERSION)

.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep

.PHONY: show
show:             ## Show the current environment.
	@echo "Running using poetry run"
	@poetry run python -V
	@poetry run python -m site

.PHONY: install
install:          ## Install the project in dev mode.
	@pip install poetry
	@poetry install


.PHONY: build
build:          ## Install the project in dev mode.
	@poetry build


.PHONY: fmt
fmt:              ## Format code using black & isort.
	poetry run python -m isort encosy/
	poetry run python -m isort tests/
	poetry run python -m isort examples/

	poetry run python -m black -l 79 encosy/
	poetry run python -m black -l 79 tests/
	poetry run python -m black -l 79 examples/

.PHONY: lint
lint:             ## Run pep8, black, mypy linters.
	poetry run flake8 encosy/
	poetry run flake8 tests/
	poetry run flake8 examples/
	poetry run black -l 79 --check encosy/
	poetry run black -l 79 --check tests/
	poetry run black -l 79 --check examples/
	poetry run mypy --ignore-missing-imports --check-untyped-defs encosy/

.PHONY: test
test:             ## Run tests and generate coverage report.
	poetry run pytest -v --cov-config .coveragerc --cov=encosy -l --tb=short --maxfail=1 tests/
	poetry run coverage xml
	poetry run coverage html

.PHONY: watch
watch:            ## Run tests on every change.
	ls **/**.py | entr poetry run pytest -s -vvv -l --tb=long --maxfail=1 tests/

.PHONY: clean
clean:            ## Clean unused files.
	@find . -name '*.pyc' -exec rm -f {} \;
	@find . -name '__pycache__' -exec rm -rf {} \;
	@find . -name 'Thumbs.db' -exec rm -f {} \;
	@find . -name '*~' -exec rm -f {} \;
	@find . -name 'mprofile_*.dat' -exec rm -f {} \;
	@find . -name '*.prof' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/
	@rm -rf docs/_build
	@rm -rf site/
	@rm -rf .coverage
	@rm -rf coverage.xml
	@rm -rf log.log

.PHONY: release
release:          ## Create a new tag for release.
	@echo "WARNING: This operation will create s version tag and push to github"
	@echo "Version? (provide the next x.y.z semver) : ${TAG}"
	@poetry run gitchangelog > HISTORY.md
	@git add encosy/VERSION HISTORY.md
	@git commit -m "release: version ${TAG} 🚀"
	@echo "creating git tag : ${TAG}"
	@git tag ${TAG}
	@git push -u origin HEAD --tags
	@echo "Github Actions will detect the new tag and release the new version."

.PHONY: docs
docs:             ## Build the documentation.
	@echo "building documentation ..."
	@poetry run mkdocs build
	@poetry run mkdocs serve