DIR_BASE=/data

export ORACLE_SID=$(cat /etc/oratab | tail -1 | awk -F: '{print$1}')

export ORAENV_ASK=NO
. oraenv 2>&1 >/dev/null

sqlplus / as sysdba 2>&1 >/tmp/create_restorepoint.$$.log <<EOF
	WHENEVER SQLERROR EXIT SQL.SQLCODE
	create restore point INIT guarantee flashback database;
EOF

if [ $? -eq 0 ]; then
	echo "Restore point INIT created"
else
	errormsg=$(cat /tmp/create_restorepoint.$$.log |grep ORA- |head -1 | sed s/^.*ORA-/ORA-/)
	echo $errormsg
	exit 1
fi
