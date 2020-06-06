FROM centos:7.7.1908

ARG RELEASE_VERSION="0.0.4"

RUN yum update -y
RUN yum install unzip -y

COPY oracle-database-preinstall-19c-1.0-1.el7.x86_64.rpm /tmp
RUN yum install -y /tmp/oracle-database-preinstall-19c-1.0-1.el7.x86_64.rpm
RUN rm /tmp/oracle-database-preinstall-19c-1.0-1.el7.x86_64.rpm
RUN sed -i "s/oracle   hard   memlock    134217728/#oracle   hard   memlock    134217728/g" /etc/security/limits.d/oracle-database-preinstall-19c.conf
RUN sed -i "s/oracle   soft   memlock    134217728/#oracle   soft   memlock    134217728/g" /etc/security/limits.d/oracle-database-preinstall-19c.conf

RUN mkdir -p /u01/app/oracle/product/19.3.0/dbhome_1
RUN mkdir -p /data/oracle
RUN chown -R oracle:oinstall /data
RUN chown -R oracle:oinstall /u01
RUN chmod -R 775 /data

COPY LINUX.X64_193000_db_home.zip /tmp
RUN su - oracle -c "unzip /tmp/LINUX.X64_193000_db_home.zip -d /u01/app/oracle/product/19.3.0/dbhome_1"
RUN rm /tmp/LINUX.X64_193000_db_home.zip
RUN su - oracle -c "cd /u01/app/oracle/product/19.3.0/dbhome_1 && ./runInstaller -ignorePrereq -waitforcompletion -silent -responseFile /u01/app/oracle/product/19.3.0/dbhome_1/install/response/db_install.rsp oracle.install.option=INSTALL_DB_SWONLY UNIX_GROUP_NAME=oinstall INVENTORY_LOCATION=/u01/app/oraInventory SELECTED_LANGUAGES=en ORACLE_BASE=/data/oracle oracle.install.db.InstallEdition=EE oracle.install.db.OSDBA_GROUP=dba oracle.install.db.OSBACKUPDBA_GROUP=dba oracle.install.db.OSDGDBA_GROUP=dba oracle.install.db.OSKMDBA_GROUP=dba oracle.install.db.OSRACDBA_GROUP=dba SECURITY_UPDATES_VIA_MYORACLESUPPORT=false DECLINE_SECURITY_UPDATES=true || true"
RUN /u01/app/oraInventory/orainstRoot.sh
RUN /u01/app/oracle/product/19.3.0/dbhome_1/root.sh

RUN yum install gcc -y
COPY 2020.01.30.slob_2.5.2.4.tar.gz /tmp
RUN gunzip /tmp/2020.01.30.slob_2.5.2.4.tar.gz
RUN tar xvf /tmp/2020.01.30.slob_2.5.2.4.tar -C /opt
RUN cd /opt/SLOB/wait_kit && make
RUN cp /opt/SLOB/wait_kit/create_sem /opt/SLOB/wait_kit/mywait /opt/SLOB/wait_kit/trigger /opt/SLOB
RUN sed -i "s/SCALE=80M/SCALE=800M/g" /opt/SLOB/slob.conf
RUN sed -i "s/DATABASE_STATISTICS_TYPE=statspack/DATABASE_STATISTICS_TYPE=awr/g" /opt/SLOB/slob.conf

COPY createDB.sh /bin
RUN chown oracle:oinstall /bin/createDB.sh
RUN chmod u+x /bin/createDB.sh
RUN ln -s /data/listener.ora /u01/app/oracle/product/19.3.0/dbhome_1/network/admin/listener.ora

COPY run.sh /bin
RUN chmod u+x /bin/run.sh
COPY startOracle.sh /bin
RUN chmod u+x /bin/startOracle.sh
RUN chown oracle:oinstall /bin/startOracle.sh

COPY startApi.sh /bin
RUN chmod u+x /bin/startApi.sh 

RUN yum install python3.x86_64 python3-devel.x86_64 which -y
RUN pip3 install  pipenv
RUN mkdir /api
COPY /api/. /api
RUN chown -R oracle:oinstall /api/web/sh
ENV LC_ALL en_US.utf8
ENV LANG en_US.utf8
RUN cd /api && pipenv install

RUN yum install epel-release -y
RUN yum install supervisor.noarch -y
RUN sed -i -- 's/nodaemon=false/nodaemon=true/' /etc/supervisord.conf
RUN sed -i -- 's/;\[inet_http_server\]/\[inet_http_server\]/' /etc/supervisord.conf
RUN sed -i -- 's/;port=127.0.0.1:9001/port=\*:9001/' /etc/supervisord.conf
RUN sed -i -- 's/;stopwaitsecs=10/stopwaitsecs=600/' /etc/supervisord.conf
COPY *.ini /etc/supervisord.d/

EXPOSE 1521
EXPOSE 9001
EXPOSE 8000

CMD ["/usr/bin/supervisord", "--configuration=/etc/supervisord.conf"]