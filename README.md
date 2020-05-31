# oraDocker

Oracle Docker image for OraTune project.

## Build an image

Download LINUX.X64_193000_db_home.zip from Oracle website into ./docker_build/oracle19/0.0.7

```
docker build -t sebcb1/oracle19:0.0.4 ./docker_build/oracle19/0.0.4
```

You can export your image:
```
docker save -o oracle19_0.0.4.tar sebcb1/oracle19
```

## Manage a database

### Create a database (by default TEST)

```
mkdir -p /docker/oracle/TEST/data
touch /docker/oracle/TEST/oratab
chown -R 54321:54321  /docker/oracle/TEST
docker run -v /docker/oracle/TEST/data:/data  -v /docker/oracle/TEST/oratab:/etc/oratab  -it sebcb1/oracle19:0.0.4 run.sh createDB
```

### Start and stop the container

```
docker-compose up -d ora
docker-compose stop ora
docker-compose start ora
```

### List of API

Start the dababase: 
```
curl -X PATCH -H "Content-Type: application/json" http://192.168.33.30:8080/database/startup
{"returncode": 0, "status": "FINISHED", "msg": "Database TEST started\n", "errormsg": ""}
```

Stop the dababase: 
```
curl -X PATCH -H "Content-Type: application/json" http://192.168.33.30:8080/database/shutdown
{"returncode": 0, "status": "FINISHED", "msg": "Database TEST shuted down\n", "errormsg": ""}
```

Flashback the dababase: 
```
curl -X PATCH -H "Content-Type: application/json" http://192.168.33.30:8080/database/flashbackdatabase
{"returncode": 0, "status": "FINISHED", "msg": "Database flashed back to restore point INIT\n", "errormsg": ""}
```

Launch replay:
```
curl -X PATCH  -d '{"name": "BENCHMARK"}' -H "Content-Type: application/json" http://192.168.33.30:8080/database/startreplay
{"returncode": 0, "status": "RUNNING", "id": 1, "msg": "", "errormsg": ""}
```

Check status of replay:
```
curl -X GET -H "Content-Type: application/json" http://192.168.33.30:8080/database/statusreplay/1
{"returncode": 0, "status": "FINISHED", "replay_status": "IN PROGRESS", "id": 1}
```

Get metrics from replay:
```
curl -X GET  -H "Content-Type: application/json" http://192.168.33.30:8080/database/metricsreplay/1
{"returncode": 1, "errormsg": "Replay not completed", "msg": "", "status": "FAILED"}
```


### Delete a database

```
echo "" > /docker/oracle/TEST/oratab
rm -rf /docker/oracle/TEST/data/*
```

### Manage supervisor

Theses ressources are managed by the supervisor.

- oracale db
- oracle listener
- django server

You can manage these resource by the website or directly in commande line.

```
docker-compose exec ora bash
supervisorctl
status
start oracle
stop oracle 
```

TRhe website listens on port 9001.

### Other commands

```
docker-compose logs ora
docker-compose exec ora bash
```

### Prepare and run benchmark

Edit /opt/SLOB/slob.conf:
```
DATABASE_STATISTICS_TYPE=awr
SCALE=800M
```

To prepare data:
```
cd /opt/SLOB
sqlplus / as sysdba
@/opt/SLOB/misc/ts.sql
exit

./setup.sh IOPS 8
```

To run the becnhmark:
```
cd /opt/SLOB
./runit.sh 8
```

### Capture and replay the benchmark with RAT

Connect on docker container:
```
docker-compose exec ora bash
su - oracle
. oraenv
mkdir /data/capture
```

```
sqlplus / as sysdba
create directory capture_dir as '/data/capture';
execute DBMS_WORKLOAD_CAPTURE.START_CAPTURE(name=>'BENCHMARK', dir=>'CAPTURE_DIR');

```

Check capture status:
```
select ID,
NAME,
STATUS,
CAPTURE_SIZE CSIZE,
TRANSACTIONS TRANS
from DBA_WORKLOAD_CAPTURES;
```

Run the benchmark:
```
sh /api/web/sh/run_benchmark.sh
```

To stop the capture:
```
execute DBMS_WORKLOAD_CAPTURE.FINISH_CAPTURE (timeout => 0,Reason  => 'Capture finished OK');
```

Preprocess the capture:
```
execute DBMS_WORKLOAD_REPLAY.PROCESS_CAPTURE (capture_dir =>'CAPTURE_DIR');
```

Now you can create the restore point:
```
create restore point INIT guarantee flashback database;
```

Now you can replay:
```
execute DBMS_WORKLOAD_REPLAY.INITIALIZE_REPLAY (replay_name =>'BENCHMARK', replay_dir=>'CAPTURE_DIR');
select id, name, STATUS, DBTIME,AWR_BEGIN_SNAP,AWR_END_SNAP from dba_workload_replays;
execute DBMS_WORKLOAD_REPLAY.PREPARE_REPLAY (synchronization => TRUE);
wrc system/manager  mode=calibrate  replaydir=/data/capture
wrc system/manager mode=replay replaydir=/data/capture
execute DBMS_WORKLOAD_REPLAY.START_REPLAY ();
```


## Updates

Version 0.0.1 - 02/05/2020 
- Inital version

Version 0.0.2 - 14/05/2020 
- Pfile will be created correctly after creating the db
- Docker hostname is automatically set in listener.ora
- The database uses OMF
- Add an API server (django)
	- Add http://<ip>:8080/database/shutdown
	- Add http://<ip>:8080/database/startup

Version 0.0.3 - 24/05/2020 
- Add SLOB in the image
- Benchmark initialized when DB is created
- Json result for API is normalized
- Add api:
	- database/createrestorepoint
	- database/flashbackdatabase
	- database/runbenchmark
- Databse is created in archivelog mode
- db_recovery_file_dest_size and db_recovery_file_dest are used

Version 0.0.4 - 31/05/2020
- Update run_benchmark.sh with correct log file name and return message
- Add the capture of benchamrk with RAT when the database is created with its restore point INIT
- Add api:
	- database/startreplay
	- database/statusreplay
	- /database/metricsreplay
- Add script to start API server with oracle env
- Improve API erros

## Some links

https://github.com/therealkevinc/SLOB_distribution
https://kevinclosson.net/2017/07/25/step-by-step-slob-installation-and-quick-test-guide-for-amazon-web-services-rds-for-oracle/


