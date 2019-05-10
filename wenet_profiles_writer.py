""" Module to write profiles to db
"""
import numpy as np

from wenet_user_profile_db import set_profile


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
            set_profile(user, profile)
