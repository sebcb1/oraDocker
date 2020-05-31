import subprocess
import logging
import logging.config
from django.views.decorators.csrf import csrf_exempt 
from django.http import JsonResponse
import csv
import json
import cx_Oracle
import time

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
def start_replay(request):
    try:
        headers = request.META
        result = {}
    
        if request.method == "PATCH":
            data = json.loads(request.body)    
            if 'name' not in data:
                result["returncode"]=1
                result["errormsg"]="Data must contain key 'name'"
                return JsonResponse(result)

            try:
                connection = cx_Oracle.connect('system', 'manager', "localhost/TEST")
                cursor = connection.cursor()
                cursor.execute("begin DBMS_WORKLOAD_REPLAY.INITIALIZE_REPLAY (replay_name =>'%s', replay_dir=>'CAPTURE_DIR'); end;" % (data['name']) )
                cursor.execute("begin DBMS_WORKLOAD_REPLAY.PREPARE_REPLAY (synchronization => TRUE); end;" )

                subprocess.Popen('su - oracle -c "sh /api/web/sh/start_wrc.sh"', universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)
                time.sleep( 5 )


                cursor.execute("begin DBMS_WORKLOAD_REPLAY.START_REPLAY (); end;" )

                cursor.execute("select id from dba_workload_replays where name=:name and STATUS='IN PROGRESS'", name=data['name'])
                row = cur.fetchone()
                id_replay = row[0]

                cursor.close()
                connection.close()

            except cx_Oracle.DatabaseError as e:
                result["returncode"]=1
                result["status"]="FAIL"
                result["errormsg"]=str(e)
                return JsonResponse(result)
         
        
            result["returncode"]=0
            result["status"]="RUNNING"
            result["id"]=id_replay
            return JsonResponse(result)


        else:
            result["returncode"]=1
            result["errormsg"]="Only PATCH method supported"
            return JsonResponse(result)

    except:
            result["returncode"]=1
            result["errormsg"]=sys.exc_info()[0]
            return JsonResponse(result)        


@csrf_exempt
def db_startup(request):

    headers = request.META
    
    if request.method == "PATCH":
        output = []

        cp = subprocess.run('su - oracle -c "sh /api/web/sh/startup.sh"', universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)

        result = {}
        result["returncode"]=cp.returncode
        result["status"]="FINISH"
        if cp.returncode==0:
            result["msg"]=cp.stdout
            result["errormsg"]=""
        else:
            result["msg"]="Failed to start database"
            result["errormsg"]=cp.stdout
        return JsonResponse(result)

@csrf_exempt
def db_shutdown(request):

    headers = request.META
    
    if request.method == "PATCH":
        output = []

        cp = subprocess.run('su - oracle -c "sh /api/web/sh/shutdown.sh"', universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)

        result = {}
        result["returncode"]=cp.returncode
        result["status"]="FINISH"
        if cp.returncode==0:
            result["msg"]=cp.stdout
            result["errormsg"]=""
        else:
            result["msg"]="Failed to shutdown database"
            result["errormsg"]=cp.stdout
        return JsonResponse(result)

@csrf_exempt
def create_restorepoint(request):

    headers = request.META
    
    if request.method == "PATCH":
        output = []

        cp = subprocess.run('su - oracle -c "sh /api/web/sh/create_restorepoint.sh"', universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)

        result = {}
        result["returncode"]=cp.returncode
        result["status"]="FINISH"
        if cp.returncode==0:
            result["msg"]=cp.stdout
            result["errormsg"]=""
        else:
            result["msg"]="Failed to create restore point INIT"
            result["errormsg"]=cp.stdout
        return JsonResponse(result)        

@csrf_exempt
def flashback_database(request):

    headers = request.META
    
    if request.method == "PATCH":
        output = []

        cp = subprocess.run('su - oracle -c "sh /api/web/sh/flashback_database.sh"', universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)

        result = {}
        result["returncode"]=cp.returncode
        result["status"]="FINISH"
        if cp.returncode==0:
            result["msg"]=cp.stdout
            result["errormsg"]=""
        else:
            result["msg"]="Failed to flashback database to INIT"
            result["errormsg"]=cp.stdout
        return JsonResponse(result)   

@csrf_exempt
def run_benchmark(request):

    headers = request.META
    
    if request.method == "PATCH":
        output = []

        cp = subprocess.run('su - oracle -c "sh /api/web/sh/run_benchmark.sh"', universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)

        result = {}
        result["returncode"]=cp.returncode
        result["status"]="FINISH"
        if cp.returncode==0:
            result["msg"]=cp.stdout
            result["errormsg"]=""
        else:
            result["msg"]="Failed to run becnhmark"
            result["errormsg"]=cp.stdout
        return JsonResponse(result)         