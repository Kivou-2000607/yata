#!/bin/bash

# pull image
docker pull dpage/pgadmin4
# create container
docker run -p 5555:80 --name pgadmin -e 'PGADMIN_DEFAULT_EMAIL=user@domain.com' -e 'PGADMIN_DEFAULT_PASSWORD=SuperSecret' -d dpage/pgadmin4

# stop/start container
docker stop pgadmin
docker start pgadmin
