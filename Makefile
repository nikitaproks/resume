run-dev:
	docker compose -f docker-compose.dev.yml up --build

stop-dev:
	docker compose -f docker-compose.dev.yml down

makemigrations:
	sh -c "cd server && poetry run python manage.py makemigrations"


test:
	test-server

test-server:
	docker compose -f docker-compose.dev.yml up -d db
	docker compose -f docker-compose.dev.yml up -d server --build
	docker compose exec server poetry run python manage.py test tests
	docker compose exec server poetry run pytest tests
	docker compose down

test-scheduler:
	cd scheduler && poetry run pytest tests


lint-server:
	sh -c "cd server && poetry run mypy ."