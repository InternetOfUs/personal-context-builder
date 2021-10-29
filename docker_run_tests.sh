#! /bin/sh
docker run -v wenet-data:/data -e PCB_DATA_FOLDER=/data -e PCB_REDIS_HOST=wenet-redis docker.idiap.ch/wenet/personal_context_builder ./run_tests.sh $@