""" Module to write profiles to db
"""
import numpy as np

from wenet_user_profile_db import set_profile
from wenet_data_loading import MockWenetSourceLabels, MockWenetSourceLocations
from wenet_analysis_models import SimpleLDA
from wenet_analysis import BagOfWordsVectorizer


class ProfileWritter(object):
    def __init__(self, locations_source, labels_source, model_instance, bow_vectorizer):
        self._locations_source = locations_source
        self._labels_source = labels_source
        self._model_instance = model_instance
        self._bow_vectorizer = bow_vectorizer

    def update_profiles(self):
        users_locations = self._locations_source.get_locations_all_users()
        for user, locations in users_locations.items():
            X = self._bow_vectorizer.vectorize(locations)
            res = self._model_instance.predit(X)
            profile = np.mean(res, axis=0)
            self.update_profile(user, profile)

    def update_profile(self, user, profile):
        set_profile(user, profile)


class ProfileWritterFromMock(ProfileWritter):
    def __init__(self):
        source_locations = MockWenetSourceLocations()
        source_labels = MockWenetSourceLabels(source_locations)
        model_instance = SimpleLDA().load(filename="mock_lda.p")
        bow_instance = BagOfWordsVectorizer.load(filename="mock_bow.p")
        super().__init__(source_locations, source_labels, model_instance, bow_instance)

    def update_profile(self, user, profile):
        print("mock - update profile of user {} with {}".format(user, str(profile)))
