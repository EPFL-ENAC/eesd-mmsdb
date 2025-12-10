install:
	uvx pre-commit install --install-hooks
	cd backend && make install
	cd frontend && npm install
	touch .env

lint:
	uvx pre-commit run --all-files
	cd frontend && npm run lint && npm run format

run-backend:
	cd backend && make run

run-frontend:
	cd frontend && npm run dev

test:
	cd backend && make test

generate-low-quality-models:
	cd scripts && uv venv --allow-existing && uv run python decrease_quality.py ../backend/data/original ../backend/data/downscaled

fix-walls-shift:
	cd scripts && uv venv --allow-existing && uv run python fix_wall_shift.py ../backend/data/downscaled

build-walls-from-stones:
	cd scripts && uv venv --allow-existing && uv run python build_walls_from_stones.py ../backend/data/original
