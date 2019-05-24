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
from wenet_user_profile_db import DatabaseProfileHandler
import config
import datetime
from pprint import pprint


class WenetApp(object):
    def __init__(self, app_name=config.DEFAULT_APP_NAME):
        self._app = Sanic(app_name)
        self._app.add_route(UserProfile.as_view(), "/routines/<user_id>/")
        self._app.add_route(UserProfiles.as_view(), "/routines/")

    def run(self, host=config.DEFAULT_APP_INTERFACE, port=config.DEFAULT_APP_PORT):
        self._app.run(host, port)


class UserProfile(HTTPMethodView):
    async def get(self, request, user_id):
        routine = DatabaseProfileHandler.get_instance().get_profile(user_id)
        if routine is not None:
            return json({user_id: routine})
        else:
            raise NotFound(f"user_id {user_id} not found in the routines database")


class UserProfiles(HTTPMethodView):
    async def get(self, request):
        routines = DatabaseProfileHandler.get_instance().get_all_profiles()
        return json(routines)
