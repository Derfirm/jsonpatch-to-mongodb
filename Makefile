POETRY ?= $(HOME)/.poetry/bin/poetry

.PHONY: install-poetry
install-poetry:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

.PHONY: install-packages
install-packages:
	$(POETRY) install -vv $(opts)

.PHONY: install
install: install-poetry install-packages

.PHONY: update
update:
	$(POETRY) update -v

.PHONY: fmt
fmt:
	$(POETRY) run black .
	$(POETRY) run isort .

.PHONY: test
test:
	$(POETRY) run pytest
