"""
Config for the project
"""

from os import environ
from collections import defaultdict

MAINTENER = "william.droz@idiap.ch"

DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEFAULT_LOG_FILE = "wenet.log"

DEFAULT_SEMANTIC_DB_NAME = "semantic_db"

DEFAULT_PROFILE_MANAGER_URL = "https://wenet.u-hopper.com/dev/profile_manager"
DEFAULT_STREAMBASE_BATCH_URL = "https://wenet.u-hopper.com/dev/streambase/data/"
# How many hours before re-updating the profiles with the semantic routines
DEFAULT_PROFILE_MANAGER_UPDATE_CD_H = 24

DEFAULT_GOOGLE_API_KEY_FILE = "google_api_key.txt"

DEFAULT_LOGGER_FORMAT = "%(asctime)s - Wenet %(name)s - %(levelname)s - %(message)s"
DEFAULT_SANIC_LOGGER_FORMAT = "%(asctime)s - Wenet (%(name)s)[%(levelname)s][%(host)s]: %(request)s %(message)s %(status)d %(byte)d"
DEFAULT_LOGGER_LEVEL = 20  # info

DEFAULT_STAYPOINTS_TIME_MIN_MS = 5 * 60 * 1000
DEFAULT_STAYPOINTS_TIME_MAX_MS = 4 * 60 * 60 * 1000
DEFAULT_STAYPOINTS_DISTANCE_MAX_M = 200

DEFAULT_STAYREGION_DISTANCE_THRESHOLD_M = 200
DEFAULT_STAYREGION_INC_DELTA = 0.000001

DEFAULT_USERPLACE_TIME_MAX_DELTA_MS = 5 * 60 * 1000
DEFAULT_USERPLACE_STAY_POINT_SAMPLING = 5 * 60 * 1000

DEFAULT_APP_NAME = "wenet_personal_context_builder"
DEFAULT_APP_INTERFACE = "0.0.0.0"
DEFAULT_APP_PORT = 80

DEFAULT_VIRTUAL_HOST = ""
DEFAULT_VIRTUAL_HOST_LOCATION = ""

DEFAULT_REDIS_HOST = "wenet-redis"
DEFAULT_REDIS_PORT = 6379

DEFAULT_REALTIME_REDIS_HOST = "wenet-realtime-redis"
DEFAULT_REALTIME_REDIS_PORT = 6379

# up to 16 (0-15) locations in default Redis settings
# Format {ModelClassName}:{PipelineClassName}
DEFAULT_REDIS_DATABASE_MODEL_0 = "SimpleLDA:PipelineBOW"
DEFAULT_REDIS_DATABASE_MODEL_1 = "SimpleBOW:PipelineBOW"
DEFAULT_REDIS_DATABASE_MODEL_2 = "SimpleHDP:PipelineWithCorpus"

DEFAULT_REGION_MAPPING_FILE = "wenet_regions_mapping.json"

DEFAULT_DATA_FOLDER = "."

# Shouldn't be used
DEFAULT_GENERIC_MODEL_NAME = "last_model.p"
DEFAULT_BOW_MODEL_FILE = "last_bow_vectorizer.p"

# will contain mapping for models
MAP_DB_TO_MODEL = dict()
MAP_MODEL_TO_DB = dict()

MAP_PIPELINE_TO_MAP_MODEL_TO_DB = defaultdict(dict)


def _update_parameters_from_env():
    """update the config values from env"""
    for k, v in globals().items():
        if k.startswith("DEFAULT_"):
            if k in environ:
                new_v = type(v)(environ[k])
                print(
                    "Parameters {} was updated from {} to {} by environment override".format(
                        k, v, new_v
                    )
                )
                globals()[k] = new_v


def _update_parameters_if_virtual_host():
    """Update parameter if virtual host is defined"""
    if "VIRTUAL_HOST" in environ:
        globals()["DEFAULT_VIRTUAL_HOST"] = environ["VIRTUAL_HOST"]
        print("VIRTUAL_HOST set to {}".format(environ["VIRTUAL_HOST"]))

    if "VIRTUAL_HOST_LOCATION" in environ:
        globals()["DEFAULT_VIRTUAL_HOST_LOCATION"] = environ["VIRTUAL_HOST_LOCATION"]
        print(
            "VIRTUAL_HOST_LOCATION set to {}".format(environ["VIRTUAL_HOST_LOCATION"])
        )


def _update_redis_database_index_mapping(MAP_DB_TO_MODEL, MAP_MODEL_TO_DB):
    """fill two dict to map Redis DB <--> model classes"""
    for k, v in globals().items():
        if k.startswith("DEFAULT_REDIS_DATABASE_MODEL_"):
            number = int(k.split("_")[-1])
            model, pipeline = v.split(":")
            MAP_DB_TO_MODEL[number] = v
            MAP_MODEL_TO_DB[v] = number
            MAP_PIPELINE_TO_MAP_MODEL_TO_DB[pipeline][model] = number


# update the config by using env
_update_parameters_from_env()
_update_parameters_if_virtual_host()
_update_redis_database_index_mapping(MAP_DB_TO_MODEL, MAP_MODEL_TO_DB)
