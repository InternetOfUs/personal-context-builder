from sanic.views import HTTPMethodView
from sanic.exceptions import NotFound
from sanic.response import json
from sanic import Blueprint

from personal_context_builder.wenet_user_profile_db import (
    DatabaseProfileHandler,
    DatabaseProfileHandlerMock,
)
from personal_context_builder import wenet_analysis_models
from personal_context_builder.wenet_analysis import closest_users, compare_routines
from personal_context_builder import config


def create_routines_bp(virtual_host_location, is_mock=False):
    """create blueprint that handle /routines/ and /routines/<user_id>/ paths
    Args:
    virtual_host_location -- virtual host location (can be provided by nginx) e. g. /devel/wenet/
    is_mock -- if true, use mocked components
    Return:
    the Blueprint instance that handle these paths
    """
    routines_bp = Blueprint("routines", url_prefix=virtual_host_location)
    if is_mock:
        routines_bp.add_route(
            SemanticRoutine.as_view(),
            "/semantic_routines/<user_id>/<weekday:number>/<time>/",
        )
        routines_bp.add_route(
            SemanticRoutineTransitionEntering.as_view(),
            "/semantic_routines_transition/entering/<user_id>/<weekday:number>/<label>/",
        )
        routines_bp.add_route(
            SemanticRoutineTransitionLeaving.as_view(),
            "/semantic_routines_transition/leaving/<user_id>/<weekday:number>/<label>/",
        )
        routines_bp.add_route(UserProfileMock.as_view(), "/routines/<user_id>/")
        routines_bp.add_route(UserProfilesMock.as_view(), "/routines/")
        routines_bp.add_route(
            ClosestUsersMock.as_view(), "/closest/<lat:number>/<lng:number>/<N:number>/"
        )
        routines_bp.add_route(
            CompareRoutinesMock.as_view(), "/compare_routines/<user>/<model>/"
        )
    else:
        routines_bp.add_route(
            SemanticRoutineMock.as_view(),
            "/semantic_routines/<user_id>/<weekday:number>/<time>/",
        )
        routines_bp.add_route(
            SemanticRoutineTransitionEnteringMock.as_view(),
            "/semantic_routines_transition/entering/<user_id>/<weekday:number>/<label>/",
        )
        routines_bp.add_route(
            SemanticRoutineTransitionLeavingMock.as_view(),
            "/semantic_routines_transition/leaving/<user_id>/<weekday:number>/<label>/",
        )
        routines_bp.add_route(UserProfile.as_view(), "/routines/<user_id>/")
        routines_bp.add_route(UserProfiles.as_view(), "/routines/")
        routines_bp.add_route(
            ClosestUsers.as_view(), "/closest/<lat:number>/<lng:number>/<N:number>/"
        )
        routines_bp.add_route(
            CompareRoutines.as_view(), "/compare_routines/<user>/<model>/"
        )
    return routines_bp


def create_available_models_bp(virtual_host_location):
    """create blueprint that handle /models/ path
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
        models = [
            model_name.split(":")[0] for model_name in config.MAP_MODEL_TO_DB.keys()
        ]
        for model_name in models:
            res[model_name] = getattr(wenet_analysis_models, model_name).__doc__
        return json(res)


class UserProfileMock(HTTPMethodView):
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
            routine = DatabaseProfileHandlerMock.get_instance(
                db_index=db_index
            ).get_profile(user_id)
            if routine is not None:
                res[model_name] = {user_id: routine}
            else:
                raise NotFound(f"user_id {user_id} not found in the routines database")
        return json(res)


class UserProfilesMock(HTTPMethodView):
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
            routines = DatabaseProfileHandlerMock.get_instance(
                db_index=db_index
            ).get_all_profiles()
            res[model_name] = routines
        return json(res)


class ClosestUsers(HTTPMethodView):
    async def get(self, request, lat, lng, N):
        res = dict()
        distance_user_location = closest_users(lat, lng, int(N), is_mock=False)
        for distance, user_location in distance_user_location:
            res[user_location._user] = distance
        return json(res)


class ClosestUsersMock(HTTPMethodView):
    async def get(self, request, lat, lng, N):
        res = dict()
        distance_user_location = closest_users(lat, lng, N, is_mock=True)
        for distance, user_location in distance_user_location:
            res[user_location._user] = distance
        return json(res)


class CompareRoutinesMock(HTTPMethodView):
    async def get(self, request, user, model):
        res = dict()
        if "users" in request.args:
            users = request.args["users"]
            res = compare_routines(user, users, model, is_mock=True)
        return json(res)


class CompareRoutines(HTTPMethodView):
    async def get(self, request, user, model):
        res = dict()
        if "users" in request.args:
            users = request.args["users"]
            res = compare_routines(user, users, model, is_mock=False)
        return json(res)


class SemanticRoutine(HTTPMethodView):
    async def get(self, request, user_id, weekday, time):
        res = dict()
        #  TODO get results
        res["user_id"] = user_id
        res["weekday"] = weekday
        res["label_distribution"] = [
            {
                "label": {
                    "name": "HOME",
                    "semantic_class": 3,
                    "latitude": 0,
                    "longitude": 0,
                },
                "score": 0.6,
            },
            {
                "label": {
                    "name": "WORK",
                    "semantic_class": 4,
                    "latitude": 0,
                    "longitude": 0,
                },
                "score": 0.4,
            },
        ]
        res["confidence"] = 0.8
        return json(res)


class SemanticRoutineMock(HTTPMethodView):
    async def get(sself, request, user_id, weekday, time):
        res = dict()
        #  TODO get results
        res["user_id"] = user_id
        res["weekday"] = weekday
        res["label_distribution"] = [
            {
                "label": {
                    "name": "HOME",
                    "semantic_class": 3,
                    "latitude": 0,
                    "longitude": 0,
                },
                "score": 0.6,
            },
            {
                "label": {
                    "name": "WORK",
                    "semantic_class": 4,
                    "latitude": 0,
                    "longitude": 0,
                },
                "score": 0.4,
            },
        ]
        res["confidence"] = 0.8
        return json(res)


class SemanticRoutineTransitionEntering(HTTPMethodView):
    async def get(self, request, user_id, weekday, label):
        res = dict()
        #  TODO get results
        res["user_id"] = user_id
        res["weekday"] = weekday
        res["transition_time"] = "07:10"
        res["label"] = label
        res["confidence"] = 0.7
        return json(res)


class SemanticRoutineTransitionEnteringMock(HTTPMethodView):
    async def get(self, request, user_id, weekday, label):
        res = dict()
        #  TODO get results
        res["user_id"] = user_id
        res["weekday"] = weekday
        res["transition_time"] = "07:10"
        res["label"] = label
        res["confidence"] = 0.7
        return json(res)


class SemanticRoutineTransitionLeaving(HTTPMethodView):
    async def get(self, request, user_id, weekday, label):
        res = dict()
        #  TODO get results
        res["user_id"] = user_id
        res["weekday"] = weekday
        res["transition_time"] = "17:00"
        res["label"] = label
        res["confidence"] = 0.8
        return json(res)


class SemanticRoutineTransitionLeavingMock(HTTPMethodView):
    async def get(self, request, user_id, weekday, label):
        res = dict()
        #  TODO get results
        res["user_id"] = user_id
        res["weekday"] = weekday
        res["transition_time"] = "17:00"
        res["label"] = label
        res["confidence"] = 0.8
        return json(res)
