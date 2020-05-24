#!/bin/sh

if [ "$1" = "createDB" ]; then
	su - oracle -c 'createDB.sh $2'
fi