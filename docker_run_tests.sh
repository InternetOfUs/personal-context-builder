#! /bin/sh
docker run -v wenet-data:/data -e DEFAULT_DATA_FOLDER=/data -e DEFAULT_REDIS_HOST=redis --network=docker1 personalcontextbuilder_wenet ./run_tests.sh $@