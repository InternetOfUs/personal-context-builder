""" Fastapi app for wenet

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,
"""
from fastapi import Depends, FastAPI, HTTPException
from personal_context_builder.wenet_fastapi_models import (
    EmbeddedModelName,
    EmbeddedRoutineOut,
)
from personal_context_builder import config, wenet_analysis_models
from personal_context_builder.wenet_analysis import closest_users, compare_routines
from personal_context_builder.wenet_user_profile_db import (
    DatabaseProfileHandler,
    DatabaseProfileHandlerMock,
)
import uvicorn
import personal_context_builder.config

from typing import Optional, List

app = FastAPI()


@app.get(
    "/routines/",
    tags=["User's embedded routines"],
    response_model=Optional[EmbeddedRoutineOut],
)
def routines(models: Optional[List[str]] = None):
    res = dict()
    if config.PCB_MOCK_DATABASEHANDLER:
        DatabaseProfileHandler = DatabaseProfileHandlerMock
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
        routines = DatabaseProfileHandler.get_instance(
            db_index=db_index
        ).get_all_profiles()
        res[model_name] = routines
    return res


def run(
    app: FastAPI = app,
    host: str = config.PCB_APP_INTERFACE,
    port: int = config.PCB_APP_PORT,
):

    uvicorn.run(app, host=host, port=port)
