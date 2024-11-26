.PHONY: build up

clear_images:
	docker images -f "dangling=true" -q | xargs docker rmi

clear_volumes:
	docker volume ls -qf "dangling=true" | xargs docker volume rm

up:
	docker-compose up --build

req: # Создание/обновление файла requirements.txt в /app
	poetry export -f requirements.txt --output app/requirements.txt --without-hashes