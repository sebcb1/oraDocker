#!/bin/sh

DIR_BASE=/data

export ORACLE_SID=$(cat /etc/oratab | tail -1 | awk -F: '{print$1}')
export ORAENV_ASK=NO
. oraenv

cd /api/web
pipenv run ./manage.py runserver 0.0.0.0:8000