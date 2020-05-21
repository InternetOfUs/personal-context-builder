""" Module responsibles to communicate with Wenet profile manager, to fill the profiles with
    the routines
"""
from personal_context_builder import config
from regions_builder.data_loading import BaseSourceLocations, BaseSourceLabels
from regions_builder.models import LocationPoint, UserPlaceTimeOnly, UserLocationPoint
from personal_context_builder.wenet_logger import create_logger
from personal_context_builder import wenet_exceptions
import datetime
import pandas as pd
import requests
from collections import defaultdict
from pprint import pprint
import json
from requests.exceptions import RequestException

_LOGGER = create_logger(__name__)

# TODO change me remove this once data is ok
GPS_STR_FAKE = """{
  "userId": "1",
  "experimentId": "Wenet",
  "properties": [
    {
      "locationeventpertime": [
        {
          "experimentId": "Wenet",
          "userId": "1",
          "timestamp": 201908252359000,
          "point": {
            "latitude": 22.1492,
            "longitude": -101.03609,
            "altitude": 1845.29208
          }
        }
      ]
    }
  ]
}"""


class Label(object):
    def __init__(self, name, semantic_class, latitude, longitude):
        self.name = name
        self.semantic_class = semantic_class
        self.latitude = latitude
        self.longitude = longitude


class ScoredLabel(object):
    def __init__(self, score, label):
        self.label = label
        self.score = score


class PersonalBehavior(object):
    def __init__(self, user_id, weekday, confidence):
        self.user_id = user_id
        self.weekday = weekday
        self.confidence = confidence
        self.label_distribution = defaultdict(list)

    def fill(self, routines):
        #  TODO something with routines
        pass


class StreamBaseLocationsLoader(BaseSourceLocations):
    def __init__(self, name="Streambase locations loader", last_days=14):
        super().__init__(name)

        # TODO change me to get all users
        users = [str(x) for x in range(1, 9)]
        self._url = config.DEFAULT_STREAMBASE_BATCH_URL
        self._users_locations = dict()
        date_to = datetime.datetime.now()
        date_from = date_to - datetime.timedelta(hours=24 * last_days)
        date_to_str = date_to.strftime("%Y%m%d")
        date_from_str = date_from.strftime("%Y%m%d")
        gps_streambase = json.loads(GPS_STR_FAKE)
        parameters = dict()
        # TODO change me to get token from partner?
        parameters["Authorization"] = "Authorization"
        parameters["from"] = date_from_str
        parameters["to"] = date_to_str
        parameters["properties"] = "locationeventpertime"
        for user in users:
            user_url = self._url + user
            self._users_locations[user] = None
            try:
                r = requests.get(user_url, data=parameters)
                if r.code == 200:
                    _LOGGER.debug(
                        f"request to stream base success for user {user} -  {r.json()}"
                    )
                else:
                    _LOGGER.warn(
                        f"request to stream base failed for user {user} with code {r.code}"
                    )
            except RequestException:
                _LOGGER.warn(f"request to stream base failed for user {user}")

            if self._users_locations[user] is None:
                # TODO change me remove this once data is ok
                _LOGGER.debug("USE FAKE DATA MIMICK STREAMBASE")
                self._users_locations[user] = self._gps_streambase_to_user_locations(
                    gps_streambase, user
                )
        if len(self._users_locations) < 1:
            raise wenet_exceptions.WenetStreamBaseLocationsError()
        _LOGGER.info("StreamBase locations loaded")

    @staticmethod
    def _gps_streambase_to_user_locations(gps_streambase, user):
        def _get_only_gps_locations(gps_streambase):
            for _property in gps_streambase["properties"]:
                for obj in _property["locationeventpertime"]:
                    yield obj

        locations = []
        locationeventpertime_list = _get_only_gps_locations(gps_streambase)
        for locationeventpertime in locationeventpertime_list:
            lat = locationeventpertime["point"]["latitude"]
            lng = locationeventpertime["point"]["longitude"]
            timestamp = locationeventpertime["timestamp"]

            try:
                pts_t = datetime.datetime.fromtimestamp(timestamp)
            except Exception as e:
                #  They dont use unix timestamp...
                # TODO change me when ppl respect unix timestamp...........
                _LOGGER.warn(
                    "invalid timestamp format from streambase - will try to use anyway"
                )
                pts_t = datetime.datetime.strptime(str(timestamp)[:-3], "%Y%m%d%H%M%S")

            location = UserLocationPoint(pts_t, lat, lng, user=user)
            locations.append(location)
        return locations

    def get_users(self):
        return list(self._users_locations.keys())

    def get_locations(self, user_id, max_n=None):
        return self._users_locations[user_id][:max_n]

    def get_locations_all_users(self, max_n=None):
        return [
            l for locations in self._users_locations.values() for l in locations[:max_n]
        ]


def update_profiles():
    pass


def update_profile(routines, profile_id, url=config.DEFAULT_PROFILE_MANAGER_URL):
    profile_url = url + f"/profiles/{profile_id}"
    personal_behaviors = []
    #  r = requests.put(profile_url, data={"personalBehaviors": personal_behaviors})
    print(f"send to {profile_url}: \n")
    for p in personal_behaviors:
        pprint(p)

    print()
