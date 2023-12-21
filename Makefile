run-dev:
	docker compose -f docker-compose.dev.yml up --build

makemigrations:
	sh -c "cd server && python manage.py makemigrations"

migrate:
	docker compose start db
	sh -c "cd server && python manage.py makemigrations"
	docker compose stop db