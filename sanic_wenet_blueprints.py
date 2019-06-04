from sanic.views import HTTPMethodView
from sanic.exceptions import NotFound
from sanic.response import json
from sanic import Blueprint
from sanic_openapi import doc

from wenet_user_profile_db import DatabaseProfileHandler
import wenet_analysis_models
import config


def create_routines_bp(virtual_host_location):
    routines_bp = Blueprint("routines", url_prefix=virtual_host_location)
    routines_bp.add_route(
        UserProfile.as_view(), "/routines/<user_id>/", strict_slashes=True
    )
    routines_bp.add_route(UserProfiles.as_view(), "/routines/", strict_slashes=True)
    return routines_bp


def create_available_models_bp(virtual_host_location):
    models_bp = Blueprint("available models", url_prefix=virtual_host_location)
    models_bp.add_route(AvailableModels.as_view(), "/models/", strict_slashes=True)
    return models_bp


class UserProfile(HTTPMethodView):
    @doc.summary("Fetches a routine by user_id")
    @doc.produces([{"model": {"user": list}}])
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
