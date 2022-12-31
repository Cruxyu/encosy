.ONESHELL:
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")
USING_POETRY=$(shell grep "tool.poetry" pyproject.toml && echo "yes")

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
	@poetry run maturin develop


.PHONY: build
build:          ## Install the project in dev mode.
	@poetry build
	@poetry run maturin develop


.PHONY: fmt
fmt:              ## Format code using black & isort.
	poetry run python -m isort pyecs/
	poetry run python -m black -l 79 pyecs/
	poetry run python -m black -l 79 tests/

.PHONY: lint
lint:             ## Run pep8, black, mypy linters.
	poetry run flake8 pyecs/
	poetry run black -l 79 --check pyecs/
	poetry run black -l 79 --check tests/
	poetry run mypy --ignore-missing-imports pyecs/

.PHONY: test
test:             ## Run tests and generate coverage report.
	poetry run pytest -v --cov-config .coveragerc --cov=pyecs -l --tb=short --maxfail=1 tests/
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
	@read -p "Version? (provide the next x.y.z semver) : " TAG
	@echo "$${TAG}" > pyecs/VERSION
	@poetry run gitchangelog > HISTORY.md
	@git add pyecs/VERSION HISTORY.md
	@git commit -m "release: version $${TAG} 🚀"
	@echo "creating git tag : $${TAG}"
	@git tag $${TAG}
	@git push -u origin HEAD --tags
	@echo "Github Actions will detect the new tag and release the new version."

.PHONY: docs
docs:             ## Build the documentation.
	@echo "building documentation ..."
	@poetry run mkdocs build
	URL="site/index.html"; xdg-open $$URL || sensible-browser $$URL || x-www-browser $$URL || gnome-open $$URL