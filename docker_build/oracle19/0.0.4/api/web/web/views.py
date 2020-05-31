import subprocess
import logging
import logging.config
from django.views.decorators.csrf import csrf_exempt 
from django.http import JsonResponse
import csv
import json
import cx_Oracle
import time
import sys

LOGGING_CONFIG = None
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
    # root logger
        '': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
})

logger = logging.getLogger(__name__)

@csrf_exempt
def metrics_replay(request, id):
    try:
        headers = request.META
        result = {}
    
        if request.method == "GET":
            connection = cx_Oracle.connect('system', 'manager', "localhost/TEST")
            cursor = connection.cursor()

            cursor.execute("select count(*) from dba_workload_replays where id=:id", id=id)
            row = cursor.fetchone()
            if row[0] == 0:
                result["returncode"]=1
                result["errormsg"]="No replay found"
                return JsonResponse(result)                

            cursor.execute("select STATUS, AWR_BEGIN_SNAP, AWR_END_SNAP from dba_workload_replays where id=:id", id=id)
            row = cursor.fetchone()
            status = row[0]
            awr_bsnap = row[1]
            awr_esnap = row[2]

            cursor.execute("select round(((select VALUE from DBA_HIST_SYS_TIME_MODEL where SNAP_ID=:end and STAT_NAME='DB time')-(select VALUE from DBA_HIST_SYS_TIME_MODEL where SNAP_ID=:begin and STAT_NAME='DB time'))/1000000) from dual", begin=awr_bsnap, end=awr_esnap)
            row = cursor.fetchone()
            dbtime = row[0]


            cursor.close()
            connection.close()


            if status != 'COMPLETED':
                result["returncode"]=1
                result["errormsg"]="Replay not completed"
                result["msg"]="" 
                result["status"]='FAILED'
                return JsonResponse(result)


            result["returncode"]=0
            result["status"]='FINISHED'
            result["id"]=id
            result["dbtime"]=dbtime
            return JsonResponse(result)

        else:
            result["returncode"]=1
            result["errormsg"]="Only GET method supported"
            return JsonResponse(result)

    except cx_Oracle.DatabaseError as e:
        result["returncode"]=1
        result["errormsg"]=str(e)
        result["msg"]=""   
        return JsonResponse(result) 
    except Exception as e:
        result["returncode"]=1
        result["errormsg"]=str(e)
        result["msg"]=""   
        return JsonResponse(result) 

@csrf_exempt
def status_replay(request, id):
    try:
        headers = request.META
        result = {}
    
        if request.method == "GET":
            connection = cx_Oracle.connect('system', 'manager', "localhost/TEST")
            cursor = connection.cursor()

            cursor.execute("select count(*) from dba_workload_replays where id=:id", id=id)
            row = cursor.fetchone()
            if row[0] == 0:
                result["returncode"]=1
                result["errormsg"]="No replay found"
                return JsonResponse(result)                

            cursor.execute("select STATUS, AWR_BEGIN_SNAP, AWR_END_SNAP from dba_workload_replays where id=:id", id=id)
            row = cursor.fetchone()
            status = row[0]
            awr_bsnap = row[1]
            awr_esnap = row[2]

            cursor.close()
            connection.close()

            result["returncode"]=0
            result["status"]='FINISHED'
            result["replay_status"]=status
            result["id"]=id
            if status == 'COMPLETED':
                result['awr_begin_snap'] = awr_bsnap
                result['awr_end_snap'] = awr_esnap
            return JsonResponse(result)

        else:
            result["returncode"]=1
            result["errormsg"]="Only GET method supported"
            return JsonResponse(result)

    except cx_Oracle.DatabaseError as e:
        result["returncode"]=1
        result["errormsg"]=str(e)
        return JsonResponse(result) 
    except Exception as e:
        result["returncode"]=1
        result["errormsg"]=str(e)
        return JsonResponse(result) 

@csrf_exempt
def start_replay(request):
    try:
        headers = request.META
        result = {}
    
        if request.method == "PATCH":
            data = json.loads(request.body)    
            if 'name' not in data:
                result["returncode"]=1
                result["errormsg"]="Data must contain key 'name'"
                result["status"]="FAILED"
                result["msg"]="" 
                return JsonResponse(result)

            connection = cx_Oracle.connect('system', 'manager', "localhost/TEST")
            cursor = connection.cursor()
            cursor.execute("begin DBMS_WORKLOAD_REPLAY.INITIALIZE_REPLAY (replay_name =>'%s', replay_dir=>'CAPTURE_DIR'); end;" % (data['name']) )
            cursor.execute("begin DBMS_WORKLOAD_REPLAY.PREPARE_REPLAY (synchronization => TRUE); end;" )

            subprocess.Popen('su - oracle -c "sh /api/web/sh/start_wrc.sh"', universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)
            time.sleep( 5 )


            cursor.execute("begin DBMS_WORKLOAD_REPLAY.START_REPLAY (); end;" )

            cursor.execute("select id from dba_workload_replays where name=:name and STATUS='IN PROGRESS'", name=data['name'])
            row = cursor.fetchone()
            id_replay = row[0]

            cursor.close()
            connection.close()
        
            result["returncode"]=0
            result["status"]="RUNNING"
            result["id"]=id_replay
            result["msg"]=""   
            result["errormsg"]=""
            return JsonResponse(result)

        else:
            result["returncode"]=1
            result["errormsg"]="Only PATCH method supported"
            result["status"]="FAILED"
            result["msg"]="" 
            return JsonResponse(result)

    except cx_Oracle.DatabaseError as e:
        result["returncode"]=1
        result["errormsg"]=str(e)
        result["status"]="FAILED"
        result["msg"]=""         
        return JsonResponse(result) 
    except Exception as e:
        result["returncode"]=1
        result["errormsg"]=str(e)
        result["status"]="FAILED"
        result["msg"]=""         
        return JsonResponse(result)        


@csrf_exempt
def db_startup(request):
    try:
        headers = request.META
    
        if request.method == "PATCH":
            output = []

            cp = subprocess.run('su - oracle -c "sh /api/web/sh/startup.sh"', universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)

            result = {}
            result["returncode"]=cp.returncode
            result["status"]="FINISHED"
            if cp.returncode==0:
                result["msg"]=cp.stdout
                result["errormsg"]=""
            else:
                result["msg"]="Failed to start database"
                result["errormsg"]=cp.stdout
            return JsonResponse(result)

    except Exception as e:
        result["returncode"]=1
        result["errormsg"]=str(e)
        result["status"]="FAILED"
        result["msg"]=""         
        return JsonResponse(result)         

@csrf_exempt
def db_shutdown(request):
    try:
        headers = request.META
    
        if request.method == "PATCH":
            output = []

            cp = subprocess.run('su - oracle -c "sh /api/web/sh/shutdown.sh"', universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)

            result = {}
            result["returncode"]=cp.returncode
            result["status"]="FINISHED"
            if cp.returncode==0:
                result["msg"]=cp.stdout
                result["errormsg"]=""
            else:
                result["msg"]="Failed to shutdown database"
                result["errormsg"]=cp.stdout
                result["status"]="FAILED"
            return JsonResponse(result)

    except Exception as e:
        result["returncode"]=1
        result["errormsg"]=str(e)
        result["status"]="FAILED"
        result["msg"]=""        
        return JsonResponse(result)         

@csrf_exempt
def create_restorepoint(request):
    try:
        headers = request.META
    
        if request.method == "PATCH":
            output = []

            cp = subprocess.run('su - oracle -c "sh /api/web/sh/create_restorepoint.sh"', universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)

            result = {}
            result["returncode"]=cp.returncode
            result["status"]="FINISHED"
            if cp.returncode==0:
                result["msg"]=cp.stdout
                result["errormsg"]=""
            else:
                result["msg"]="Failed to create restore point INIT"
                result["errormsg"]=cp.stdout
            return JsonResponse(result)   

    except Exception as e:
        result["returncode"]=1
        result["errormsg"]=str(e)
        result["status"]="FAILED"
        result["msg"]=""        
        return JsonResponse(result)  

@csrf_exempt
def flashback_database(request):
    try:
        headers = request.META
    
        if request.method == "PATCH":
            output = []

            cp = subprocess.run('su - oracle -c "sh /api/web/sh/flashback_database.sh"', universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)

            result = {}
            result["returncode"]=cp.returncode
            result["status"]="FINISHED"
            if cp.returncode==0:
                result["msg"]=cp.stdout
                result["errormsg"]=""
            else:
                result["msg"]="Failed to flashback database to INIT"
                result["errormsg"]=cp.stdout
            return JsonResponse(result)   

    except Exception as e:
        result["returncode"]=1
        result["errormsg"]=str(e)
        result["status"]="FAILED"
        result["msg"]=""
        return JsonResponse(result)             

@csrf_exempt
def run_benchmark(request):
    try:
        headers = request.META
    
        if request.method == "PATCH":
            output = []

            cp = subprocess.run('su - oracle -c "sh /api/web/sh/run_benchmark.sh"', universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)

            result = {}
            result["returncode"]=cp.returncode
            result["status"]="FINISHED"
            if cp.returncode==0:
                result["msg"]=cp.stdout
                result["errormsg"]=""
            else:
                result["msg"]="Failed to run becnhmark"
                result["errormsg"]=cp.stdout
            return JsonResponse(result)         
    except Exception as e:
        result["returncode"]=1
        result["errormsg"]=str(e)
        result["msg"]=""
        result["status"]="FAILED"
        return JsonResponse(result)            