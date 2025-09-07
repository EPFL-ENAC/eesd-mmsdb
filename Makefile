install:
	pre-commit install --install-hooks
	cd backend && make install
	cd frontend && npm install
	touch .env

lint:
	pre-commit run --all-files
	cd frontend && npm run lint && npm run format

run-backend:
	cd backend && make run

run-frontend:
	cd frontend && npm run dev

test:
	cd backend && make test
