server_down:
	podman-compose -f server/docker-compose.yml down -t 1

server_build:
	podman-compose -f server/docker-compose.yml build 

server_up: server_down server_build
	podman-compose -f server/docker-compose.yml up

server_bash: server_down server_build
	podman-compose -f server/docker-compose.yml run server bash

pip_install: server_down server_build
	podman-compose -f server/docker-compose.yml run server \
		python -m pip install -e .[dev]
