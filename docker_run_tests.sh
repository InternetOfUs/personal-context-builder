#! /bin/sh
docker run -v wenet-data:/data -e DEFAULT_DATA_FOLDER=/data -e DEFAULT_REDIS_HOST=wenet-redis --network=docker1 docker.idiap.ch/wenet/personal_context_builder ./run_tests.sh $@