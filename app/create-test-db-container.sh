#!/usr/bin/env bash

set -e

# remove test db container if exists
if [ "$(docker ps -aq -f name=revamp_test_db)" ]; then
  docker container rm -f revamp_test_db
fi

# create new test db container
docker run --name revamp_test_db -e POSTGRES_USER="${POSTGRES_USER:?}" -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD:?}" -e POSTGRES_DB="${POSTGRES_DB:?}" -p 5432:5432 -d postgres

# wait for container to initialize
sleep 5s

# activate venv if given
if [ "${VENV}" ]; then
  source "./${VENV}/bin/activate"
fi

# initialize test db with data
python ./app/initial_data.py
