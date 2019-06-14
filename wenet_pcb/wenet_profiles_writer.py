""" Module to write profiles to db
"""
import numpy as np

from wenet_pcb.wenet_user_profile_db import DatabaseProfileHandlerMock
from wenet_pcb.wenet_data_loading import MockWenetSourceLabels, MockWenetSourceLocations
from wenet_pcb.wenet_analysis_models import SimpleLDA
from wenet_pcb.wenet_analysis import BagOfWordsVectorizer
from wenet_pcb.wenet_trainer import BaseBOWTrainer


class ProfileWritter(object):
    def __init__(
        self,
        locations_source,
        labels_source,
        model_instance,
        bow_trainer,
        database_instance,
    ):
        """ Handle the writting in the db of the profiles
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
        """ update all profiles
        """
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

    def update_profile(self, user, profile):
        """ update a single profile
        Args:
            user: user to update
            profile: profile to use
        """
        self._database_instance.set_profile(user, profile)


class ProfileWritterFromMock(ProfileWritter):
    def __init__(
        self,
        source_locations=None,
        source_labels=None,
        model_instance=None,
        bow_trainer=None,
        database_instance=None,
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