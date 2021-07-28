""" Fastapi app for wenet

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,
"""
from typing import List, Optional, Type, Union

import uvicorn  # type: ignore
from fastapi import Depends, FastAPI, HTTPException, Query  # type: ignore

import personal_context_builder.config
from personal_context_builder import config, wenet_analysis_models
from personal_context_builder.wenet_analysis import closest_users, compare_routines
from personal_context_builder.wenet_fastapi_models import (
    EmbeddedModelName,
    EmbeddedModels,
    EmbeddedRoutineOut,
    EmbeddedRoutinesDist,
    SemanticRoutine,
)
from personal_context_builder.wenet_user_profile_db import (
    DatabaseProfileHandler,
    DatabaseProfileHandlerBase,
    DatabaseProfileHandlerMock,
)

tags_metadata = [
    {
        "name": "User's embedded routines",
        "description": "embedded routines of the user",
    },
    {
        "name": "User's semantic routines",
        "description": "(MOCKED) semantic routines of the user",
    },
]

description = """Component that handle the personal context of the users <br /> <img
    src="https://drive.google.com/uc?id=1iF39kFa5ZcYKadCzynHvRkt6ftj59aHc" />
    <br />Routines are an embedded representation of the user habits.
"""

title = "WeNet - personal_context_builder"

app = FastAPI(openapi_tags=tags_metadata, description=description, title=title)


@app.get(
    "/routines/",
    tags=["User's embedded routines"],
    response_model=EmbeddedRoutineOut,
)
async def routines(models: Optional[List[str]] = Query(None)):
    res = dict()
    handler_to_use: Optional[Type[DatabaseProfileHandlerBase]]
    if config.PCB_MOCK_DATABASEHANDLER:
        handler_to_use = DatabaseProfileHandlerMock
    else:
        handler_to_use = DatabaseProfileHandler
    if models is not None:
        models_set = set(models)
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
        routines = handler_to_use.get_instance(db_index=db_index).get_all_profiles()
        res[model_name] = routines
    return res


@app.get(
    "/routines/{user_id}",
    tags=["User's embedded routines"],
    response_model=EmbeddedRoutineOut,
)
async def routines_for_user(user_id: str, models: Optional[List[str]] = Query(None)):
    res = dict()
    handler_to_use: Optional[Type[DatabaseProfileHandlerBase]] = None
    if config.PCB_MOCK_DATABASEHANDLER:
        handler_to_use = DatabaseProfileHandlerMock
    else:
        handler_to_use = DatabaseProfileHandler
    if models is not None:
        models_set = set(models)
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
        routines = handler_to_use.get_instance(db_index=db_index).get_profile(user_id)
        res[model_name] = {user_id: routines}
    return res


@app.get(
    "/models/",
    tags=["User's embedded routines"],
    response_model=EmbeddedModels,
)
async def get_available_models():
    res = dict()
    models = [model_name.split(":")[0] for model_name in config.MAP_MODEL_TO_DB.keys()]
    for model_name in models:
        res[model_name] = getattr(wenet_analysis_models, model_name).__doc__
    return res


@app.get(
    "/compare_routines/{user_id}/{model}/",
    tags=["User's embedded routines"],
    response_model=EmbeddedRoutinesDist,
)
async def get_compare_routines(
    user_id: str, model: str, users: List[str] = Query(None)
):
    res = compare_routines(
        user_id, users, model, is_mock=config.PCB_MOCK_DATABASEHANDLER
    )
    return res


@app.get(
    "/semantic_routines/{user_id}/{weekday}/{time}/",
    tags=["User's semantic routines"],
    response_model=SemanticRoutine,
)
async def get_semantic_routines(user_id: str, weekday: int, time: str):
    label_distribution = [
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
    return SemanticRoutine(
        user_id=user_id,
        weekday=weekday,
        label_distribution=label_distribution,
        confidence=0.8,
    )


def run(
    app: FastAPI = app,
    host: str = config.PCB_APP_INTERFACE,
    port: int = config.PCB_APP_PORT,
):  # pragma: no cover

    uvicorn.run(app, host=host, port=port)
