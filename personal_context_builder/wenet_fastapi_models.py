""" module for fastapi models

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,

"""
from pydantic import BaseModel
from typing import Dict, List


class EmbeddedModelName(BaseModel):
    """name of the model"""

    __root__ = str


class EmbeddedRoutineOut(BaseModel):
    __root__: Dict[str, Dict[str, List[float]]]

    class Config:
        schema_extra = {
            "example": {
                "SimpleLDA": {"mock_user_1": [0, 1, 0, 0.5, 1]},
                "SimpleBOW": {"mock_user_1": [1, 1, 0, 0.5, 1]},
            }
        }


class EmbeddedModels(BaseModel):
    __root__: Dict[str, str]
    """descriptions of the embedded models"""

    class Config:
        schema_extra = {
            "example": {
                "SimpleLDA": "Simple LDA over all the users, with 15 topics",
                "SimpleBOW": "Bag-of-words approach, compute the mean of all days",
                "SimpleHDP": "Bag-of-words approach, compute the mean of all days",
            }
        }
