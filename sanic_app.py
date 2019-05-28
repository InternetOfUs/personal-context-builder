from sanic import Sanic
from sanic.views import HTTPMethodView
from sanic.response import text
from sanic.exceptions import NotFound
from sanic.response import json
from wenet_models import LocationPoint, StayPoint
from wenet_algo import (
    estimate_stay_points,
    estimate_stay_regions,
    estimate_stay_regions_per_day,
)
import wenet_analysis_models
from wenet_user_profile_db import DatabaseProfileHandler
import config
import datetime
from pprint import pprint


class WenetApp(object):
    def __init__(
        self,
        app_name=config.DEFAULT_APP_NAME,
        virtual_host=config.DEFAULT_VIRTUAL_HOST,
        virtual_host_location=config.DEFAULT_VIRTUAL_HOST_LOCATION,
    ):
        self._app = Sanic(app_name)
        self._app.add_route(
            UserProfile.as_view(), virtual_host_location + "/routines/<user_id>/"
        )
        self._app.add_route(
            UserProfiles.as_view(), virtual_host_location + "/routines/"
        )
        self._app.add_route(
            AvailableModels.as_view(), virtual_host_location + "/models/"
        )

    def run(self, host=config.DEFAULT_APP_INTERFACE, port=config.DEFAULT_APP_PORT):
        self._app.run(host, port)


class UserProfile(HTTPMethodView):
    async def get(self, request, user_id):
        res = dict()
        for db_index, model_name in config.MAP_DB_TO_MODEL.items():
            routine = DatabaseProfileHandler.get_instance(
                db_index=db_index
            ).get_profile(user_id)
            if routine is not None:
                res[model_name] = {user_id: routine}
            else:
                raise NotFound(f"user_id {user_id} not found in the routines database")
        return json(res)


class UserProfiles(HTTPMethodView):
    async def get(self, request):
        res = dict()
        for db_index, model_name in config.MAP_DB_TO_MODEL.items():
            routines = DatabaseProfileHandler.get_instance(
                db_index=db_index
            ).get_all_profiles()
            res[model_name] = routines
        return json(res)


class AvailableModels(HTTPMethodView):
    async def get(self, request):
        res = dict()
        for model_name in config.MAP_MODEL_TO_DB.keys():
            res[model_name] = getattr(wenet_analysis_models, model_name).__doc__
        return json(res)
