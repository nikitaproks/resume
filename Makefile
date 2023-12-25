run-dev:
	docker compose -f docker-compose.dev.yml up --build

makemigrations:
	sh -c "cd server && poetry run python manage.py makemigrations"
