"""
Config for the project

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,

"""

from collections import defaultdict
from os import environ
from typing import Dict

MAINTAINER = "william.droz@idiap.ch"

PCB_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
PCB_LOG_FILE = "wenet.log"

PCB_SEMANTIC_DB_NAME = "semantic_db"

# dev or prod
PCB_ENV = "dev"

# Set to true for unittesting
PCB_IS_UNITTESTING = False

# Set to true to mock PCB_MOCK_DATABASEHANDLER
PCB_MOCK_DATABASEHANDLER = False

# will replace {} by PCB_ENV at runtime
PCB_PROFILE_MANAGER_URL = "https://wenet.u-hopper.com/{}/profile_manager"
PCB_PROFILE_MANAGER_OFFSET = 0
PCB_PROFILE_MANAGER_LIMIT = 1000000
PCB_STREAMBASE_BATCH_URL = "https://wenet.u-hopper.com/{}/streambase/data"
PCB_USER_LOCATION_URL = "https://lab.idiap.ch/devel/hub/wenet/users_locations/"
#  PCB_STREAMBASE_BATCH_URL = "https://wenet.u-hopper.com/{}/api/common/data/"
# How many hours before re-updating the profiles with the semantic routines

PCB_GENERATOR_START_URL = "http://streambase4.disi.unitn.it:8190/generator/start"
PCB_GENERATOR_STOP_URL = "http://streambase4.disi.unitn.it:8190/generator/stop"

PCB_PROFILE_MANAGER_UPDATE_CD_H = 24
PCB_PROFILE_MANAGER_UPDATE_HAS_LOCATIONS = True

PCB_GOOGLE_API_KEY_FILE = "google_api_key.txt"

# Should be provided at runtime using COMP_AUTH_KEY
PCB_WENET_API_KEY = ""

PCE_WENET_SENTRY_KEY = ""

#  PCB_LOGGER_FORMAT = "%(asctime)s - Wenet %(name)s - %(levelname)s - %(message)s"
PCB_LOGGER_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
PCB_SANIC_LOGGER_FORMAT = "%(asctime)s - Wenet (%(name)s)[%(levelname)s][%(host)s]: %(request)s %(message)s %(status)d %(byte)d"
PCB_LOGGER_LEVEL = 40  # error

PCB_STAYPOINTS_TIME_MIN_MS = 5 * 60 * 1000
PCB_STAYPOINTS_TIME_MAX_MS = 4 * 60 * 60 * 1000
PCB_STAYPOINTS_DISTANCE_MAX_M = 200

PCB_STAYREGION_DISTANCE_THRESHOLD_M = 200
PCB_STAYREGION_INC_DELTA = 0.000001

PCB_USERPLACE_TIME_MAX_DELTA_MS = 5 * 60 * 1000
PCB_USERPLACE_STAY_POINT_SAMPLING = 5 * 60 * 1000

PCB_APP_NAME = "wenet_personal_context_builder"
PCB_APP_INTERFACE = "0.0.0.0"
PCB_APP_PORT = 80

# Virtualhost, can be overwritten vy .venv
PCB_VIRTUAL_HOST = ""
PCB_VIRTUAL_HOST_LOCATION = ""

PCB_REDIS_HOST = "wenet-redis"
PCB_REDIS_PORT = 6379

PCB_REALTIME_REDIS_HOST = "wenet-realtime-redis"
PCB_REALTIME_REDIS_PORT = 6379

PCB_WENET_API_HOST = "wenet-api"

# up to 16 (0-15) locations in default Redis settings
# Format {ModelClassName}:{PipelineClassName}
PCB_REDIS_DATABASE_MODEL_0 = "SimpleLDA:PipelineBOW"
PCB_REDIS_DATABASE_MODEL_1 = "SimpleBOW:PipelineBOW"
PCB_REDIS_DATABASE_MODEL_2 = "SimpleHDP:PipelineWithCorpus"

PCB_REGION_MAPPING_FILE = "wenet_regions_mapping.json"

PCB_DATA_FOLDER = "."

# Shouldn't be used
PCB_GENERIC_MODEL_NAME = "last_model.p"
PCB_BOW_MODEL_FILE = "last_bow_vectorizer.p"

# will contain mapping for models
MAP_DB_TO_MODEL: Dict[int, str] = dict()
MAP_MODEL_TO_DB: Dict[str, int] = dict()

MAP_PIPELINE_TO_MAP_MODEL_TO_DB: Dict[str, Dict[str, int]] = defaultdict(dict)


def _update_parameters_from_env():  # pragma: no cover
    """update the config values from env"""
    for k, v in globals().items():
        if k.startswith("PCB_"):
            if k in environ:
                new_v = type(v)(environ[k])
                print(
                    "Parameters {} was updated from {} to {} by environment override".format(
                        k, v, new_v
                    )
                )
                globals()[k] = new_v


def _update_env_for_partners_url():  # pragma: no cover
    urls = ["PCB_PROFILE_MANAGER_URL", "PCB_STREAMBASE_BATCH_URL"]
    for url in urls:
        globals()[url] = globals()[url].format(PCB_ENV)


def _update_api_key():  # pragma: no cover
    """update the api key using env"""
    if "COMP_AUTH_KEY" in environ:
        globals()["PCB_WENET_API_KEY"] = environ["COMP_AUTH_KEY"]
        print("WENET API key setted")


def _update_parameters_if_virtual_host():  # pragma: no cover
    """Update parameter if virtual host is defined"""
    if "VIRTUAL_HOST" in environ:
        globals()["PCB_VIRTUAL_HOST"] = environ["VIRTUAL_HOST"]
        print("VIRTUAL_HOST set to {}".format(environ["VIRTUAL_HOST"]))

    if "VIRTUAL_HOST_LOCATION" in environ:
        globals()["PCB_VIRTUAL_HOST_LOCATION"] = environ["VIRTUAL_HOST_LOCATION"]
        print(
            "VIRTUAL_HOST_LOCATION set to {}".format(environ["VIRTUAL_HOST_LOCATION"])
        )


def _update_redis_database_index_mapping(
    MAP_DB_TO_MODEL: Dict, MAP_MODEL_TO_DB: Dict
):  # pragma: no cover
    """fill two dict to map Redis DB <--> model classes"""
    for k, v in globals().items():
        if k.startswith("PCB_REDIS_DATABASE_MODEL_"):
            number = int(k.split("_")[-1])
            model, pipeline = v.split(":")
            MAP_DB_TO_MODEL[number] = v
            MAP_MODEL_TO_DB[v] = number
            MAP_PIPELINE_TO_MAP_MODEL_TO_DB[pipeline][model] = number


# update the config by using env
_update_parameters_from_env()
_update_parameters_if_virtual_host()
_update_redis_database_index_mapping(MAP_DB_TO_MODEL, MAP_MODEL_TO_DB)
_update_api_key()
_update_env_for_partners_url()
