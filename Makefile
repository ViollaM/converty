
run:
	docker-compose up

stop:
	docker-compose stop

build:
	docker build -t converty_img .

entry:
	docker exec -it converty_bot bash

run_db:
	docker exec -it converty_db psql -U postgres -d converty

dump_db:
	mkdir -p db_dump/
	docker exec converty_db pg_dump -U postgres -d converty > db_dump/converty.sql
