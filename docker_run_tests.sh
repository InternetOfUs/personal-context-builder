#! /bin/sh
docker run -v wenet-data:/data -e DEFAULT_DATA_FOLDER=/data -e DEFAULT_REDIS_HOST=wenet-redis docker.idiap.ch/wenet/personal_context_builder conda run -n wenet ./run_tests.sh $@