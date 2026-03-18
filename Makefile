ifeq ($(OS),Windows_NT)
PYTHON ?= .venv/Scripts/python.exe
NPM ?= npm.cmd
else
PYTHON ?= .venv/bin/python
NPM ?= npm
endif

.PHONY: up down backend-test web-test release-clear-dashboard release-seed-dashboard release-verify

up:
	docker compose up -d

down:
	docker compose down

backend-test:
	cd backend && $(PYTHON) -m pytest -v

web-test:
	cd web && $(NPM) run test

release-clear-dashboard:
	cd backend && $(PYTHON) -m tests.support.seed_dashboard_runtime clear

release-seed-dashboard:
	cd backend && $(PYTHON) -m tests.support.seed_dashboard_runtime seed

release-verify:
	cd backend && $(PYTHON) -m pytest -q
	cd web && $(NPM) run test
	cd web && npx tsc --noEmit
	cd web && $(NPM) run lint
	cd web && $(NPM) run build
	cd web && npx playwright test
