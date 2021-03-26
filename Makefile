VIRTUAL_ENV_PATH=venv
SKIP_VENV="${NO_VENV}"
PYPI_API_KEY :=
PYPI_REPOSITORY_URL :=
ALPHA_VERSION :=

SHELL := /bin/bash
.DEFAULT_GOAL := pre_commit

pre_commit: format lint

flake8:
	@( \
       set -e; \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Runing Flake8 checks..."; \
       flake8 ./custom_components/prana --count --statistics; \
       echo "DONE: Flake8"; \
    )

mypy:
	@( \
       set -e; \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Runing MyPy checks..."; \
       mypy --show-error-codes ./custom_components/prana; \
       echo "DONE: MyPy"; \
    )

lint: flake8 mypy

clean:
	@(rm -rf custom_components/build dist/* *.egg-info custom_components/*.egg-info .pytest_cache)

format:
	@( \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Runing Black code formater..."; \
       black ./custom_components/prana; \
       echo "DONE: Black"; \
    )

venv:
	@( \
		virtualenv $(VIRTUAL_ENV_PATH); \
		source ./venv/bin/activate; \
		pip install -r ./requirements.txt; \
	)