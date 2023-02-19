#!/bin/bash

DB_NAME=gsb23_tickets
SOURCE_FILE=scanner/source.db
TABLES_TO_DROP="django_migrations auth_group auth_group_permissions auth_permission django_admin_log django_content_type django_flatpage django_flatpage_sites django_session django_site ticketing_alloweduser ticketing_attendance ticketing_promocode ticketing_wave ticketkinds_optional_extras tickets_extras ucamwebauth_userprofile userkinds_waves users_user_permissions users_groups ticketing_ticketallocation ticketing_setting ticketkinds_waves userkind_ticketkinds"

# this script must be run in the scanner dir

# delete current state
psql postgres matias -c "drop database if exists ${DB_NAME}"

# create new database using ticket data
psql postgres matias -c "CREATE DATABASE ${DB_NAME} WITH ENCODING 'UTF8' TEMPLATE template0"
psql --quiet "${DB_NAME}" matias -c "CREATE SCHEMA IF NOT EXISTS heroku_ext AUTHORIZATION matias"
psql --quiet "${DB_NAME}" matias -c "CREATE extension IF NOT EXISTS pg_stat_statements WITH schema heroku_ext"
pg_restore -O "${SOURCE_FILE}" -d "${DB_NAME}"

# delete tables we don't care about
for table in $TABLES_TO_DROP; do
	psql --quiet "${DB_NAME}" matias -c "drop table ${table} cascade"
#	echo "dropping ${table}"
done

# migrate
. .venv/bin/activate
python manage.py migrate