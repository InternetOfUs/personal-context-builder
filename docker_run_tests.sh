#! /bin/sh
docker run -v wenet-data:/data -e PCB_DATA_FOLDER=/data -e PCB_REDIS_HOST=wenet-redis docker.idiap.ch/wenet/personal_context_builder conda run -n wenet_fastapi ./run_tests.sh $@