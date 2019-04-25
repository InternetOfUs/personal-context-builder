"""
Config for the project
"""

from os import environ

DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

DEFAULT_STAYPOINTS_TIME_MIN_MS = 5 * 60 * 1000
DEFAULT_STAYPOINTS_TIME_MAX_MS = 4 * 60 * 60 * 1000
DEFAULT_STAYPOINTS_DISTANCE_MAX_M = 200

DEFAULT_STAYREGION_DISTANCE_THRESHOLD_M = 200
DEFAULT_STAYREGION_INC_DELTA = 0.000001

DEFAULT_USERPLACE_TIME_MAX_DELTA_MS = 5 * 60 * 1000
DEFAULT_USERPLACE_STAY_POINT_SAMPLING = 5 * 60 * 1000

DEFAULT_APP_NAME = "wenet_personal_context_builder"
DEFAULT_APP_INTERFACE = "0.0.0.0"
DEFAULT_APP_PORT = 8000

DEFAULT_REDIS_HOST = "localhost"
DEFAULT_REDIS_PORT = 6379


def _update_parameters_from_env():
    """ update the config values from env
    """
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


# update the config by using env
_update_parameters_from_env()
