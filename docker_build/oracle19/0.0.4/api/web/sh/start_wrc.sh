DIR_BASE=/data
LOG_FILE=/tmp/start_wrc.$$.log

export ORACLE_SID=$(cat /etc/oratab | tail -1 | awk -F: '{print$1}')

export ORAENV_ASK=NO
. oraenv 2>&1 >/dev/null

nohup wrc system/manager replaydir=/data/capture 2>&1 >$LOG_FILE &

if [ $? -eq 0 ]; then
	sleep 5
	errormsg_count=$(cat $LOG_FILE |grep ORA- |wc -l)
	if [ $errormsg_count -eq 0 ]; then
		echo "wrc is running"
		exit 0
	else
		errormsg=$(cat $LOG_FILE |grep ORA- |head -1 | sed s/^.*ORA-/ORA-/)
		echo $errormsg
		exit 1
	fi
else
	errormsg=$(cat $LOG_FILE |grep ORA- |head -1 | sed s/^.*ORA-/ORA-/)
	echo $errormsg
	exit 1
fi
