from sanic import Sanic
from sanic import Blueprint
from sanic.exceptions import NotFound, ServerError
from sanic.response import text
import logging
from sanic_wenet_blueprints import create_available_models_bp, create_routines_bp
import config

import wenet_exceptions
from wenet_logger import create_web_logger_config, create_logger

_LOGGER_CONFIG = create_web_logger_config()


class WenetApp(object):
    """ class that create the Sanic web service
    """

    def __init__(
        self,
        app_name=config.DEFAULT_APP_NAME,
        virtual_host=config.DEFAULT_VIRTUAL_HOST,
        virtual_host_location=config.DEFAULT_VIRTUAL_HOST_LOCATION,
        is_mock=False,
    ):
        """ constructor
        Args:
        app_name -- name of the app
        virtual_host -- virtual host (can be provided by nginx) e. g. lab.idiap.ch
        virtual_host_location -- virtual host location (can be provided by nginx) e. g. /devel/wenet/
        is_mock -- if true, use mocked components
        """
        self._app = Sanic(app_name)

        routines_bp = create_routines_bp(virtual_host_location, is_mock)
        models_bp = create_available_models_bp(virtual_host_location)

        self._app.blueprint([routines_bp, models_bp])

    def run(self, host=config.DEFAULT_APP_INTERFACE, port=config.DEFAULT_APP_PORT):
        """ run the web service
        Args:
        host -- the host/interface to listen
        port -- which port to use
        """
        logging.config.dictConfig(_LOGGER_CONFIG)

        self._app.error_handler.add(NotFound, wenet_exceptions.ignore_404s)
        self._app.error_handler.add(ServerError, wenet_exceptions.server_error)

        self._app.run(host, port, configure_logging=False)
