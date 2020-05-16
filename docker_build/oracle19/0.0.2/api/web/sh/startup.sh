DIR_BASE=/data

export ORACLE_SID=$(cat /etc/oratab | tail -1 | awk -F: '{print$1}')

export ORAENV_ASK=NO
. oraenv

sqlplus / as sysdba <<EOF
	startup pfile=/data/pfile$ORACLE_SID.ora
EOF
