#!/bin/bash

set -x -e


GIT_REVISION=$(git rev-parse --verify HEAD)


docker stop $(docker ps -a -q) || true
docker ps || true

docker kill $(docker ps -a -q) || true
docker rm $(docker ps -a -q) || true
docker ps || true


pwd


find . -name "*.pyc" -print -exec rm -fr {} \;


rm -fr airflow

mkdir airflow
cp -R ../* airflow

docker build --rm -t localbuild/airflow-test:$GIT_REVISION .
docker tag localbuild/airflow-test:$GIT_REVISION localbuild/airflow-test:latest

rm -fr airflow


echo "$1"
if [ "$1" = "norun" ]; then
  echo "not running"
else
  cd ..
  docker-compose -f docker-compose.yml up
fi
