#!/bin/sh

DIR_BASE=/data
HOME=/u01/app/oracle/product/19.3.0/dbhome_1
USER=$(id |awk '{print $1}' |awk -F\( '{print $2}'|awk -F\) '{print $1}')

if [ "$USER" != "oracle" ]; then
	echo "Oracle user must be used"
	exit 0
fi	

if [ -f $DIR_BASE/system01.dbf ]; then
	echo "A database already exists"
	exit 0
fi

if [ "$1" = "" ]; then
	export ORACLE_SID=TEST
else
	export ORACLE_SID=$1
fi

echo "Creation database $ORACLE_SID"
echo "$ORACLE_SID:$HOME:N" >> /etc/oratab
export ORAENV_ASK=NO
. oraenv
orapwd file=$DIR_BASE/orapwd$ORACLE_SID password=manager force=y format=12
ln -s $DIR_BASE/orapwd$ORACLE_SID $ORACLE_HOME/dbs/orapwd$ORACLE_SID

mkdir /data/omf
cat <<EOF > $DIR_BASE/pfile$ORACLE_SID.ora
db_name=$ORACLE_SID
DB_CREATE_ONLINE_LOG_DEST_1=$DIR_BASE/omf
DB_CREATE_FILE_DEST=$DIR_BASE/omf
undo_management=AUTO
sga_target=1G
DIAGNOSTIC_DEST=$DIR_BASE
EOF

sqlplus / as sysdba <<EOF
WHENEVER SQLERROR exit
startup nomount pfile='$DIR_BASE/pfile$ORACLE_SID.ora'
CREATE DATABASE "$ORACLE_SID"
USER SYS IDENTIFIED BY manager
USER SYSTEM IDENTIFIED BY manager
LOGFILE GROUP 1 SIZE 50M,
GROUP 2 SIZE 50M,
GROUP 3 SIZE 50M
MAXLOGFILES 5
MAXLOGMEMBERS 5
MAXLOGHISTORY 50
MAXDATAFILES 100
MAXINSTANCES 1
DATAFILE SIZE 100M autoextend on
SYSAUX DATAFILE SIZE 100M autoextend on
DEFAULT TABLESPACE users datafile size 100m autoextend on
DEFAULT TEMPORARY TABLESPACE temp TEMPFILE SIZE 50m autoextend on
UNDO TABLESPACE undotbs1 DATAFILE SIZE 200M autoextend on;
@$ORACLE_HOME/rdbms/admin/catalog.sql
@$ORACLE_HOME/rdbms/admin/catproc.sql
@$ORACLE_HOME/sqlplus/admin/pupbld.sql
create spfile='$DIR_BASE/spfile$ORACLE_SID.ora' from memory;
shutdown immediate
EOF

rm $DIR_BASE/pfile$ORACLE_SID.ora
echo "spfile='$DIR_BASE/spfile$ORACLE_SID.ora'" > $DIR_BASE/pfile$ORACLE_SID.ora

cat <<EOF > $DIR_BASE/listener.ora
listener=
   (description=
   (address=(protocol=tcp)(host=localhost)(port=1521)))
sid_list_listener=
   (sid_list=
   (sid_desc=
   (oracle-home=$ORACLE_HOME)
   (sid_name=$ORACLE_SID)))
EOF
