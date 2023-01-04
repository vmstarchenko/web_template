server_down:
	podman-compose -f ./docker-compose.yml down -t 1

server_build:
	podman-compose -f ./docker-compose.yml build

server_up: server_down
	podman-compose -f ./docker-compose.yml up

server_bash: server_down server_build
	podman-compose -f ./docker-compose.yml run web bash

server_bash2:
	podman-compose -f ./docker-compose.yml exec web bash

server_test: server_down
	podman-compose -f ./docker-compose.yml run web bash etc/scripts/test.sh

server_tests: server_test

api_export_schema: server_down
	rm ./etc/api_schema.yaml -f && \
	podman-compose -f ./docker-compose.yml run web \
		python etc/scripts/export_schema.py -e etc/env/dev -o etc/api_schema.yaml

api_generate_client: api_export_schema
	rm -rf "${PWD}/var/volumes/api_clients/*" && \
	cp ./etc/api_schema.yaml "${PWD}/server/var/volumes/api_clients/api_schema.yaml" && \
	podman build etc/docker/openapitools -t local-openapitools && \
	podman run \
	    -u "${USER_ID}:${GROUP_ID}" \
		-v "${PWD}/server/var/volumes/api_clients/":/home/user/api_clients \
	    --rm local-openapitools \
		generate -c ./etc/config-typescript-axios.yaml --enable-post-process-file

db_migrations: server_down
	podman-compose -f ./docker-compose.yml run web \
        alembic --config ./alembic/alembic.ini revision --autogenerate -m "$(msg)"

db_migrate: server_down
	podman-compose -f ./docker-compose.yml run web \
        alembic --config ./alembic/alembic.ini upgrade head

db_drop_dev: server_down
	rm -f server/alembic/versions/*.py && \
	rm -f var/volumes/db/dev_db.sqlite && \
	make db_migrations && make db_migrate

clear:
	python3 -Bc "import pathlib; [p.unlink() for p in pathlib.Path('server').rglob('*.py[co]')]"
	python3 -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('server').rglob('__pycache__')]"

clean: clear

pip_install: server_down server_build
	podman-compose -f ./docker-compose.yml run web \
		python -m pip install -e .[dev]
