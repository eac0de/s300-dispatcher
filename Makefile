.PHONY: build up

clear_images:
	docker images -f "dangling=true" -q | xargs docker rmi

clear_volumes:
	docker volume ls -qf "dangling=true" | xargs docker volume rm

up:
	docker-compose up --build