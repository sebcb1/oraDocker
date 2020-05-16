
<h1>Pour créer une base par defaut (test)</h1>

Données dans le container:

<code>
docker run --name oraTEST -it sebcb1/oracle19:0.0.1 run.sh createDB
</code>

Données a l'extérieur container:
<code>
mkdir -p /docker/oracle/test/data
touch /docker/oracle/test/oratab
chown -R 54321:54321  /docker/oracle/test
docker run --name oraSeb -v /docker/oracle/test/data:/data  -v /docker/oracle/test/oratab:/etc/oratab  -it sebcb1/oracle19:0.0.1 run.sh createDB
</code>

<h1>Démarrer/Arrêt/Relance la base</h1>
<code>
docker-compose up -d oraSeb
docker-compose stop oraSeb
docker-compose start oraSeb
</code>

<h1>Autres commandes</h1>

<code>
docker-compose logs oraSeb
docker-compose exec oraSeb bash
docker run --name oraSeb -it sebcb1/oracle19:0.0.1 /bin/bash
docker save -o sebcb1_oracle19_0.0.1.tar sebcb1/oracle19
</code>

<h1>Pousser l'image vers DockerHub</h1>

<code>
docker login
docker push sebcb1/oracle19:0.0.1
</code>

<h1>Supervisor commandes</h1>

<code>
supervisorctl
status
start oracle
stop oracle
</code>

<h1>Construire l'image</h1>

<code>
docker build -t sebcb1/oracle19:0.0.1 /root/docker_build/oracle19/0.0.1
</code>


<h1>Révision</h1>

<h2>Version 0.0.1 - 02/05/2020 </h2> 

Version Initiale avec Oracle 19.3.0


pfile was create correctly after creating the db