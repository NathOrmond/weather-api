#!/bin/bash

docker-compose --profile dev down
docker-compose --profile dev up --build