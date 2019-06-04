#! /bin/sh
./production_reload.sh
#  Mock for now
./docker_train_model_production.sh --mock
./docker_update_users_production.sh