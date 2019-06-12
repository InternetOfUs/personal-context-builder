from sanic import Sanic
from sanic import Blueprint
from sanic.exceptions import NotFound
from sanic.response import text
import logging
from sanic_wenet_blueprints import create_available_models_bp, create_routines_bp
import config

import wenet_exceptions
from wenet_logger import create_web_logger_config, create_logger

_LOGGER_CONFIG = create_web_logger_config()


class WenetApp(object):
    def __init__(
        self,
        app_name=config.DEFAULT_APP_NAME,
        virtual_host=config.DEFAULT_VIRTUAL_HOST,
        virtual_host_location=config.DEFAULT_VIRTUAL_HOST_LOCATION,
    ):
        self._app = Sanic(app_name)

        routines_bp = create_routines_bp(virtual_host_location)
        models_bp = create_available_models_bp(virtual_host_location)

        self._app.blueprint([routines_bp, models_bp])

    def run(self, host=config.DEFAULT_APP_INTERFACE, port=config.DEFAULT_APP_PORT):
        logging.config.dictConfig(_LOGGER_CONFIG)

        self._app.error_handler.add(NotFound, wenet_exceptions.ignore_404s)

        self._app.run(host, port, configure_logging=False)
