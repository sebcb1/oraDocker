DIR_BASE=/data
LOG_FILE=/tmp/run_benchmark.$$.log

export ORACLE_SID=$(cat /etc/oratab | tail -1 | awk -F: '{print$1}')

export ORAENV_ASK=NO
. oraenv 2>&1 >/dev/null

cd /opt/SLOB
./runit.sh 8

if [ $? -eq 0 ]; then
	echo "Benchmark run"
else
	errormsg=$(cat $LOG_FILE |grep ORA- |head -1 | sed s/^.*ORA-/ORA-/)
	echo $errormsg
	exit 1
fi
