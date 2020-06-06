DIR_BASE=/data

export ORACLE_SID=$(cat /etc/oratab | tail -1 | awk -F: '{print$1}')

export ORAENV_ASK=NO
. oraenv 2>&1 >/dev/null

sqlplus / as sysdba 2>&1 >/tmp/shutdown.$$.log <<EOF
	WHENEVER SQLERROR EXIT SQL.SQLCODE
	shutdown immediate
EOF

if [ $? -eq 0 ]; then
	echo "Database $ORACLE_SID shuted down"
else
	errormsg=$(cat /tmp/shutdown.$$.log |grep ORA- |head -1 | sed s/^.*ORA-/ORA-/)
	echo $errormsg
	exit 1
fi
