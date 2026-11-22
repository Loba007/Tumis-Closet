.PHONY: help install backend-test backend-lint backend-check frontend-install frontend-test frontend-lint frontend-build check up render-config render-config-dry-run

help:
	@echo "Tunmis Closet — common tasks"
	@echo "  make install          Install backend (dev) and frontend dependencies"
	@echo "  make check            Run backend + frontend checks/tests/build"
	@echo "  make backend-test     Run Django tests with coverage"
	@echo "  make backend-lint     Run ruff"
	@echo "  make frontend-test    Run Vitest"
	@echo "  make frontend-lint    Run ESLint"
	@echo "  make frontend-build   Production build (requires VITE_API_URL)"
	@echo "  make up               Start the Docker Compose stack (Postgres + API)"
	@echo "  make render-config    Apply render.yaml to existing Render services (needs RENDER_API_KEY)"
	@echo "  make render-config-dry-run  Preview Render changes without applying them"

install:
	cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
	cd frontend && npm ci

backend-test:
	cd backend && .venv/bin/coverage run manage.py test && .venv/bin/coverage report

backend-lint:
	cd backend && .venv/bin/ruff check .

backend-check:
	cd backend && .venv/bin/python manage.py check
	cd backend && .venv/bin/python manage.py makemigrations --check --dry-run

frontend-install:
	cd frontend && npm ci

frontend-test:
	cd frontend && npm run test:coverage

frontend-lint:
	cd frontend && npm run lint

frontend-build:
	cd frontend && VITE_API_URL=$${VITE_API_URL:-https://api.example.com/api} npm run build

check: backend-lint backend-check backend-test frontend-lint frontend-test frontend-build

up:
	docker compose up --build

render-config:
	python3 scripts/configure_render.py

render-config-dry-run:
	python3 scripts/configure_render.py --dry-run --no-deploy
