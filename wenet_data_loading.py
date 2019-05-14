"""
Module that load locations/labels data
"""

from abc import ABC, abstractmethod
from datetime import timedelta
from datetime import datetime
from random import random
from collections import defaultdict
import hashlib
from wenet_models import UserLocationPoint, UserPlace
import config


class BaseSourceLocations(ABC):
    def __init__(self, name):
        self._name = name

    @abstractmethod
    def get_users(self):
        pass

    @abstractmethod
    def get_locations(self, user_id, max_n=None):
        pass

    @abstractmethod
    def get_locations_all_users(self, max_n=None):
        pass


class BaseSourceLabels(ABC):
    def __init__(self, name):
        self._name = name

    @abstractmethod
    def get_users(self):
        pass

    @abstractmethod
    def get_labels(self, user_id, max_n=None):
        pass

    @abstractmethod
    def get_labels_all_users(self, max_n=None):
        pass


class MockWenetSourceLocations(BaseSourceLocations):
    def __init__(self):
        super().__init__("mock wenet source locations")
        self._users_locations = {
            "mock_user_1": self._create_fake_locations("mock_user_1"),
            "mock_user_2": self._create_fake_locations("mock_user_2"),
            "mock_user_3": self._create_fake_locations("mock_user_3"),
        }

    @classmethod
    def _create_fake_locations(
        cls, user_id, nb=2000, dt_s=config.DEFAULT_STAYPOINTS_TIME_MIN_MS / 1000
    ):
        locations = []
        start_date = datetime.now()
        for _ in range(nb):
            lat = 46.109394 + (
                int(hashlib.sha224(user_id.encode("utf-8")).hexdigest(), 16) & 63
            ) * ((random() - 0.5) / 100000)
            lng = 7.084442 + (
                int(hashlib.sha224(user_id.encode("utf-8")).hexdigest(), 16) & 63
            ) * ((random() - 0.5) / 100000)
            location = UserLocationPoint(start_date, lat, lng, 0, user_id)
            locations.append(location)
            start_date = start_date - timedelta(seconds=dt_s + 1)
        return locations

    def get_users(self):
        return list(self._users_locations.keys())

    def get_locations(self, user_id, max_n=None):
        return self._users_locations[user_id]

    def get_locations_all_users(self, max_n=None):
        self._users_locations


class MockWenetSourceLabels(BaseSourceLabels):
    def __init__(self, source_locations):
        super().__init__("mock source labels")
        self._source_locations = source_locations
        self._users_labels = dict()
        for user, locations in self._source_locations.get_locations_all_users().items():
            first_loc = locations[0]
            self._users_labels[user] = UserPlace(
                first_loc._pts_t, first_loc._lat, first_loc._lng, "mock label", user
            )

    def get_users(self):
        return list(self._users_labels.keys())

    def get_labels(self, user_id, max_n=None):
        return self._users_labels[user_id]

    def get_labels_all_users(self, max_n=None):
        return self._users_labels
