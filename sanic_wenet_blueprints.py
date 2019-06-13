from sanic.views import HTTPMethodView
from sanic.exceptions import NotFound
from sanic.response import json
from sanic import Blueprint

from wenet_user_profile_db import DatabaseProfileHandler
import wenet_analysis_models
import config


def create_routines_bp(virtual_host_location):
    """ create blueprint that handle /routines/ and /routines/<user_id>/ paths
    Args:
    virtual_host_location -- virtual host location (can be provided by nginx) e. g. /devel/wenet/
    Return:
    the Blueprint instance that handle these paths
    """
    routines_bp = Blueprint("routines", url_prefix=virtual_host_location)
    routines_bp.add_route(UserProfile.as_view(), "/routines/<user_id>/")
    routines_bp.add_route(UserProfiles.as_view(), "/routines/")
    return routines_bp


def create_available_models_bp(virtual_host_location):
    """ create blueprint that handle /models/ path
    Args:
    virtual_host_location -- virtual host location (can be provided by nginx) e. g. /devel/wenet/
    Return:
    the Blueprint instance that handle /models/ path
    """
    models_bp = Blueprint("available models", url_prefix=virtual_host_location)
    models_bp.add_route(AvailableModels.as_view(), "/models/")
    return models_bp


class UserProfile(HTTPMethodView):
    async def get(self, request, user_id):
        res = dict()
        if "models" in request.args:
            models_set = set(request.args["models"])
            db_dict = dict(
                [
                    (db_index, model_name)
                    for db_index, model_name in config.MAP_DB_TO_MODEL.items()
                    if model_name in models_set
                ]
            )
        else:
            db_dict = config.MAP_DB_TO_MODEL
        for db_index, model_name in db_dict.items():
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
        if "models" in request.args:
            models_set = set(request.args["models"])
            db_dict = dict(
                [
                    (db_index, model_name)
                    for db_index, model_name in config.MAP_DB_TO_MODEL.items()
                    if model_name in models_set
                ]
            )
        else:
            db_dict = config.MAP_DB_TO_MODEL
        for db_index, model_name in db_dict.items():
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
