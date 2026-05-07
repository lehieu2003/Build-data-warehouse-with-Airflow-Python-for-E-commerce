include .env
export

to_mysql:
	docker exec -it mysql mysql -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" ${MYSQL_DATABASES}

to_mysql_root:
	docker exec -it mysql mysql -u"root" -p"${MYSQL_ROOT_PASSWORD}" ${MYSQL_DATABASES}

mysql_create:
	docker exec -it mysql mysql --local-infile=1 -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" ${MYSQL_DATABASES} -e"source /tmp/load_dataset/olist.sql"

mysql_load:
	docker exec -it mysql mysql --local-infile=1 -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" ${MYSQL_DATABASES} -e"source /tmp/load_dataset/load_data.sql"
