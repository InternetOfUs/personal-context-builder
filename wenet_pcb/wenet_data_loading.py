"""
Module that load locations/labels data
"""

from typing import List
from uuid import uuid4
from abc import ABC, abstractmethod
from datetime import timedelta
from datetime import datetime
from random import random
from collections import defaultdict
import hashlib
from wenet_pcb.wenet_models import UserLocationPoint, UserPlace, GPSPoint
from wenet_pcb import config
from wenet_pcb.wenet_realtime_user_db import (
    DatabaseRealtimeLocationsHandlerMock,
    DatabaseRealtimeLocationsHandler,
)
from wenet_pcb.wenet_user_profile_db import (
    DatabaseProfileHandler,
    DatabaseProfileHandlerMock,
)
from wenet_pcb.wenet_algo import closest_locations

from scipy import spatial


def compare_routines(
    source_user, users, model, function=spatial.distance.cosine, is_mock=False
):
    """
    compare routines of users
    Args:
        source_user: the user that will be compared to the users
        users: list of users to compare to
        model: on which model the comparison should be applied
        function: the similarity function to use
        is_mock: if true, use mocked data
    """
    model_num = config.MAP_MODEL_TO_DB[model]
    if is_mock:
        db = DatabaseProfileHandlerMock.get_instance(model_num)
    else:
        db = DatabaseProfileHandler.get_instance(model_num)
    source_routine = db.get_profile(source_user)
    routines = [db.get_profile(u) for u in users]
    routines_dist = [function(source_routine, r) for r in routines]
    res = list(zip(users, routines_dist))
    res = sorted(res, key=lambda x: -x[1])
    return dict(res)


def closest_users(lat, lng, N, is_mock=False):
    """
    give the N closest users to the point (lat, lng)
    Args:
        lat: the latitude
        lng: the longitude
        N: how many users in output
        is_mock: if true, use mocked data
    """
    point = GPSPoint(lat, lng)
    if is_mock:
        db = DatabaseRealtimeLocationsHandlerMock.get_instance()
        fake_locations = [
            MockWenetSourceLocations._create_fake_locations(str(uuid4()), nb=1)[0]
            for _ in range(3000)
        ]
        db.update(fake_locations)
    else:
        db = DatabaseRealtimeLocationsHandler.get_instance()
    users_locations = db.get_all_users().values()
    sorted_users_locations = closest_locations(point, users_locations, N=N)
    return sorted_users_locations


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
    def __init__(self, nb=2000):
        super().__init__("mock wenet source locations")
        self._users_locations = {
            "mock_user_1": self._create_fake_locations("mock_user_1", nb),
            "mock_user_2": self._create_fake_locations("mock_user_2", nb),
            "mock_user_3": self._create_fake_locations("mock_user_3", nb),
        }

    @classmethod
    def _create_fake_locations(
        cls,
        user_id,
        nb: int = 2000,
        dt_s: int = config.DEFAULT_STAYPOINTS_TIME_MIN_MS / 1000,
    ) -> List[UserLocationPoint]:
        """ class method to create some fake locations
        Args:
            user_id: the user_id to use
            nb: number of fake locations to create
            dt_s: delta time to use between each location
        Return:
            list of "fake" UserLocationPoint
        """
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
        return self._users_locations


class MockWenetSourceLabels(BaseSourceLabels):
    def __init__(self, source_locations):
        super().__init__("mock source labels")
        self._source_locations = source_locations
        self._users_labels = defaultdict(list)
        for user, locations in self._source_locations.get_locations_all_users().items():
            first_loc = locations[0]
            self._users_labels[user].append(
                UserPlace(
                    first_loc._pts_t, first_loc._lat, first_loc._lng, "mock label", user
                )
            )

    def get_users(self):
        return list(self._users_labels.keys())

    def get_labels(self, user_id, max_n=None):
        return self._users_labels[user_id]

    def get_labels_all_users(self, max_n=None):
        return self._users_labels
