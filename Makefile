ifeq ($(OS),Windows_NT)
    VENV_ACTIVATE := .venv\Scripts\activate
else
    VENV_ACTIVATE := .venv/bin/activate
endif

ifeq ($(OS),Windows_NT)
    VENV_DEV_ACTIVATE := .venv-dev\Scripts\activate
else
    VENV_DEV_ACTIVATE := .venv-dev/bin/activate
endif

.PHONY: install install-dev lint exec

SOURCE_DIRS := imagepy
MYPY_ARGS := --install-types --non-interactive --check-untyped-defs --disallow-untyped-defs --disallow-incomplete-defs --check-untyped-defs

$(VENV_ACTIVATE): requirements.txt .pre-commit-config.yaml
	python3.11 -m venv .venv
	. $(VENV_ACTIVATE) && pip install --upgrade pip==24.0 \
		&& pip install -r requirements.txt

install: $(VENV_ACTIVATE)

$(VENV_DEV_ACTIVATE):
	python3.11 -m venv .venv-dev
	. $(VENV_DEV_ACTIVATE) && pip install --upgrade pip==24.0 \
		&& pip install -r requirements.txt
	. $(VENV_DEV_ACTIVATE) && pip install -r requirements-dev.txt \
		&& pre-commit install

install-dev: $(VENV_DEV_ACTIVATE)

lint: install-dev
	. $(VENV_DEV_ACTIVATE) && black $(SOURCE_DIRS) && mypy $(SOURCE_DIRS) $(MYPY_ARGS)

exec: install-dev
	APO\venv\Scripts\pyinstaller.exe --onefile APO\src\app.py
