""" module for fastapi models

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,

"""
from pydantic import BaseModel  # type: ignore
from typing import Dict, List, Optional


class EmbeddedModelName(BaseModel):
    """name of the model"""

    __root__ = str


class EmbeddedRoutineOut(BaseModel):
    __root__: Dict[str, Optional[Dict[str, List[float]]]]

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


class Label(BaseModel):
    """Label"""

    name: str
    semantic_class: int
    latitude: float
    longitude: float


class LabelScore(BaseModel):
    """label with score"""

    label: Label
    score: float


class SemanticRoutine(BaseModel):
    """Semantic routine"""

    user_id: str
    weekday: int
    label_distribution: List[LabelScore]
    confidence: float

    class Config:
        schema_extra = {
            "example": {
                "user_id": "mock_user_1",
                "weekday": 4,
                "label_distribution": [
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
                ],
                "confidence": 0.8,
            }
        }


class EmbeddedRoutinesDist(BaseModel):
    """Embedded routines distances from an users to some users"""

    __root__: Dict[str, float]
