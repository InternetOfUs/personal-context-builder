#! /bin/sh
./production_reload.sh
#  Mock for now
./docker_train_model.sh --mock
./docker_update_users.sh