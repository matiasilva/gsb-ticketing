#!/bin/bash

export DJANGO_SETTINGS_MODULE=settings.development

reset(){(
	rm db.sqlite3
	python3 manage.py migrate
	source import_fixtures.sh
)}

for verb in "$@"; do
  case "$verb" in
    reset) reset;;
  esac
done

export `heroku config -a gsb-ticketing -s | grep GOOGLE`