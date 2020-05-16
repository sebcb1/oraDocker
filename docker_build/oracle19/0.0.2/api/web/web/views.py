import subprocess
import logging
import logging.config
from django.views.decorators.csrf import csrf_exempt 
from django.http import JsonResponse
import csv

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
def db_startup(request):

    headers = request.META
    
    if request.method == "PATCH":
        output = []

        cp = subprocess.run('su - oracle -c "sh /api/web/sh/startup.sh"', universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = True)

        result = {}
        result["returncode"]=cp.returncode
        result["stdout"]=cp.stdout
        result["stderr"]=cp.stderr
        return JsonResponse(result)

@csrf_exempt
def db_shutdown(request):

    headers = request.META
    
    if request.method == "PATCH":
        output = []

        cp = subprocess.run('su - oracle -c "sh /api/web/sh/shutdown.sh"', universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = True)

        result = {}
        result["returncode"]=cp.returncode
        result["stdout"]=cp.stdout
        result["stderr"]=cp.stderr
        return JsonResponse(result)

