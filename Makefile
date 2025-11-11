DC := docker compose

pull:
	$(DC) pull

build:
	$(DC) build

up:
	$(DC) up

stop:
	$(DC) stop

down:
	$(DC) down

run: pull build up