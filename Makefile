ifeq ($(OS),Windows_NT)
    SUFFIX := \Scripts\activate
    ACTIVATE_COMMAND := call
    PYTHON_INTERPRETER := py -3.11
    REMOVE_CMD := rd /s /q
else
    SUFFIX := /bin/activate
    ACTIVATE_COMMAND := .
    PYTHON_INTERPRETER := python3.11
    REMOVE_CMD := rm -rf
endif

define activate_env
    $(ACTIVATE_COMMAND) $1$(SUFFIX)
endef

USER_VENV := .venv
VENV_ACTIVATE := $(USER_VENV)$(SUFFIX)
DEV_VENV := .venv-dev
DEV_VENV_ACTIVATE := $(DEV_VENV)$(SUFFIX)
EXE_VENV := .venv-exe
SOURCE_DIRS := imagepy
MYPY_ARGS := --install-types --non-interactive

.PHONY: install install-dev lint build clean

$(VENV_ACTIVATE): pyproject.toml .pre-commit-config.yaml
	$(PYTHON_INTERPRETER) -m venv $(USER_VENV)
	$(call activate_env, $(USER_VENV)) && pip install --upgrade pip==24.0 \
		&& pip install .

install: $(VENV_ACTIVATE)

$(DEV_VENV_ACTIVATE): pyproject.toml .pre-commit-config.yaml
	$(PYTHON_INTERPRETER) -m venv $(DEV_VENV)
	$(call activate_env, $(DEV_VENV)) && pip install --upgrade pip==24.0 \
		&& pip install .[dev] \
		&& pre-commit install

install-dev: $(DEV_VENV_ACTIVATE)

lint: $(DEV_VENV_ACTIVATE)
	$(call activate_env, $(DEV_VENV)) && black $(SOURCE_DIRS) && mypy $(SOURCE_DIRS) $(MYPY_ARGS)

build:
	$(PYTHON_INTERPRETER) -m venv $(EXE_VENV)
	$(call activate_env, $(EXE_VENV)) \
		&& pip install --upgrade pip==24.0 \
		&& pip install .[pyinstaller]
	$(call activate_env, $(EXE_VENV)) \
		&& pyinstaller imagepy.spec
	$(REMOVE_CMD) $(EXE_VENV)

clean:
	$(REMOVE_CMD) $(EXE_VENV) $(USER_VENV) $(DEV_VENV) build dist imagepy.egg-info
