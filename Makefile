PYTHON ?= C:/Users/win/AppData/Local/Programs/Python/Python313/python.exe
NPM ?= "C:/Program Files/nodejs/npm.cmd"

.PHONY: up down backend-test web-test

up:
	docker compose up -d

down:
	docker compose down

backend-test:
	cd backend && $(PYTHON) -m pytest -v

web-test:
	cd web && $(NPM) run test
