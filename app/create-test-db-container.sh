#!/usr/bin/env bash
docker kill $(docker ps -q)
docker run -e POSTGRES_USER=${POSTGRES_USER:?} -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?} -e POSTGRES_DB=${POSTGRES_DB:?} -p 5432:5432 -d postgres
sleep 5s
source ./${VENV:?}/bin/activate
python ./app/initial_data.py
