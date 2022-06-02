""" Module to write profiles to db

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,

"""
from typing import Any, List, Optional

import numpy as np
from regions_builder.data_loading import BaseSourceLabels  # type: ignore
from regions_builder.data_loading import (
    BaseSourceLocations,
    MockWenetSourceLabels,
    MockWenetSourceLocations,
)

from personal_context_builder.wenet_analysis import BagOfWordsVectorizer
from personal_context_builder.wenet_analysis_models import SimpleLDA
from personal_context_builder.wenet_trainer import BaseBOWTrainer
from personal_context_builder.wenet_user_profile_db import (
    DatabaseProfileHandlerBase,
    DatabaseProfileHandlerMock,
)


class ProfileWritter(object):
    def __init__(
        self,
        locations_source: BaseSourceLocations,
        labels_source: BaseSourceLabels,
        model_instance: Any,
        bow_trainer: BaseBOWTrainer,
        database_instance: DatabaseProfileHandlerBase,
    ):
        """Handle the writting in the db of the profiles
        Args:
            locations_source: data source for location
            labels_source: data source for the labels
            model_instance: instance of the model to use (ML)
            bow_trainer: Bag-Of-Words trainer to use
        """
        self._locations_source = locations_source
        self._labels_source = labels_source
        self._model_instance = model_instance
        self._bow_trainer = bow_trainer
        self._database_instance = database_instance

    def update_profiles(self):
        """update all profiles"""
        users_locations = self._locations_source.get_locations_all_users()
        for user, locations in users_locations.items():
            X = []
            bow_user = self._bow_trainer.train(user)
            for day in BagOfWordsVectorizer.group_by_days(locations, user):
                data = bow_user.vectorize(day)
                X.append(data)
            X = np.array(X).reshape(len(X), -1)
            res = self._model_instance.predict(X)
            if len(res.shape) == 2:
                profile = np.mean(res, axis=0)
            else:
                profile = res.copy()
            self.update_profile(user, profile.tolist())

    def update_profile(self, user: str, profile: List[float]):
        """update a single profile
        Args:
            user: user to update
            profile: profile to use
        """
        self._database_instance.set_profile(user, profile)


class ProfileWritterFromMock(ProfileWritter):
    def __init__(
        self,
        source_locations: Optional[BaseSourceLocations] = None,
        source_labels: Optional[BaseSourceLabels] = None,
        model_instance: Optional[Any] = None,
        bow_trainer: Optional[BaseBOWTrainer] = None,
        database_instance: Optional[DatabaseProfileHandlerBase] = None,
    ):
        if source_locations is None:
            source_locations = MockWenetSourceLocations()
        if source_labels is None:
            source_labels = MockWenetSourceLabels(source_locations)
        if model_instance is None:
            model_instance = SimpleLDA().load(filename="mock_lda.p")
        if bow_trainer is None:
            bow_trainer = bow_trainer = BaseBOWTrainer(source_locations, source_labels)
        if database_instance is None:
            database_instance = DatabaseProfileHandlerMock.get_instance()
        super().__init__(
            source_locations,
            source_labels,
            model_instance,
            bow_trainer,
            database_instance,
        )
