# oraDocker

Oracle Docker image for OraTune project.

## Build an image

Download LINUX.X64_193000_db_home.zip from Oracle website into ./docker_build/oracle19/0.0.3

```
docker build -t sebcb1/oracle19:0.0.3 ./docker_build/oracle19/0.0.3
```

You can export your image:
```
docker save -o oracle19_0.0.3.tar sebcb1/oracle19
```

## Manage a database

### Create a database (by default TEST)

```
mkdir -p /docker/oracle/TEST/data
touch /docker/oracle/TEST/oratab
chown -R 54321:54321  /docker/oracle/TEST
docker run -v /docker/oracle/TEST/data:/data  -v /docker/oracle/TEST/oratab:/etc/oratab  -it sebcb1/oracle19:0.0.3 run.sh createDB
```

### Start and stop the database

```
docker-compose up -d ora
docker-compose stop ora
docker-compose start ora
```

### Delete a database

```
cd /docker/oracle/TEST
echo "" > oratab
cd /docker/oracle/TEST/data
rm -rf *
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
./setup.sh IOPS 8
```

To run the becnhmark:
```
cd /opt/SLOB
./runit.sh 8
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


## Some links

https://github.com/therealkevinc/SLOB_distribution
https://kevinclosson.net/2017/07/25/step-by-step-slob-installation-and-quick-test-guide-for-amazon-web-services-rds-for-oracle/


