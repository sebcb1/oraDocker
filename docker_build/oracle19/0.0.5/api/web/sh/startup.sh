DIR_BASE=/data

export ORACLE_SID=$(cat /etc/oratab | tail -1 | awk -F: '{print$1}')

export ORAENV_ASK=NO
. oraenv 2>&1 >/dev/null

sqlplus / as sysdba 2>&1 >/tmp/startup.$$.log <<EOF
	WHENEVER SQLERROR EXIT SQL.SQLCODE
	startup pfile=/data/pfile$ORACLE_SID.ora
EOF

if [ $? -eq 0 ]; then
	echo "Database $ORACLE_SID started"
else
	errormsg=$(cat /tmp/startup.$$.log |grep ORA- |head -1 | sed s/^.*ORA-/ORA-/)
	echo $errormsg
	exit 1
fi
