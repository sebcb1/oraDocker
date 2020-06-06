#!/bin/sh

DIR_BASE=/data

export ORACLE_SID=$(cat /etc/oratab | tail -1 | awk -F: '{print$1}')

export ORAENV_ASK=NO
. oraenv

id
echo "ORACLE_SID: $ORACLE_SID"
echo "ORACLE_HOME: $ORACLE_HOME"

stopDB() { 
	lsnrctl stop 
	sqlplus / as sysdba <<EOF
	shutdown immediate
EOF
	
	exit 0
}

startDB() {
	sleep 10
	sqlplus / as sysdba <<EOF
	startup pfile=/data/pfile$ORACLE_SID.ora
EOF
	currenthostname=$(hostname)
	sed -i "s/localhost/${currenthostname}/" /data/listener.ora
	lsnrctl start
}

startDB

trap stopDB SIGTERM

while true ; do
    C=$(ps -ef | grep pmon | grep -v grep | wc -l)
	if [ $C -eq 0 ]; then
		exit 1
	fi
	sleep 1
done

