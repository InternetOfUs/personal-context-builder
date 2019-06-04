from sanic import Sanic
from sanic import Blueprint
from sanic_openapi import swagger_blueprint

from sanic_wenet_blueprints import create_available_models_bp, create_routines_bp
import config


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

        self._app.blueprint(
            swagger_blueprint,
            url_prefix=virtual_host_location + "/swagger/",
            strict_slashes=True,
        )

        self._app.blueprint([routines_bp, models_bp])
        self._app.config.API_HOST = virtual_host
        self._app.config.API_BASEPATH = virtual_host_location

    def run(self, host=config.DEFAULT_APP_INTERFACE, port=config.DEFAULT_APP_PORT):
        self._app.run(host, port)
