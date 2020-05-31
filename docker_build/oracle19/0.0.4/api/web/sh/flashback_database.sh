DIR_BASE=/data
LOG_FILE=/tmp/flashback_database.$$.log

export ORACLE_SID=$(cat /etc/oratab | tail -1 | awk -F: '{print$1}')

export ORAENV_ASK=NO
. oraenv 2>&1 >/dev/null

sqlplus / as sysdba 2>&1 >$LOG_FILE <<EOF
	WHENEVER SQLERROR EXIT SQL.SQLCODE
	shutdown immediate
	startup mount pfile=/data/pfile$ORACLE_SID.ora
	flashback database to restore point INIT;
	alter database open resetlogs;
EOF

if [ $? -eq 0 ]; then
	echo "Database flashed back to restore point INIT"
else
	errormsg=$(cat $LOG_FILE |grep ORA- |head -1 | sed s/^.*ORA-/ORA-/)
	echo $errormsg
	exit 1
fi
