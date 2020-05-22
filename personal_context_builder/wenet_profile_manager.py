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

# TODO change me remove this once data are ok
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

# TODO change me remove this once surveys are ok
SURVEY_STR_FAKE = """{
  "userId": "1",
  "experimentId": "Wenet",
  "properties": [
    {
      "timediariesanswers": [
        {
          "experimentId": "Wenet",
          "userId": "1",
          "instanceid": "f161dee2a122af926a9c4285275800942d128c34",
          "answer": [
            [
              {
                "cnt": "I am at home",
                "qid": 2,
                "aid": 3,
                "cid": -1
              }
            ]
          ],
          "answerduration": 20142,
          "answertimestamp": 20190909010129450,
          "day": 20190910,
          "instancetimestamp": 20190911201814344,
          "notificationtimestamp": 20190911201816910,
          "payload": [
            {
              "payload": {},
              "qid": 1
            }
          ]
        }
      ]
    },
    {
      "timediariesquestions": [
        {
          "experimentId": "Wenet",
          "userId": "1",
          "instanceid": "f161dee2a122af926a9c4285275800942d128c34",
          "question": {
            "q": {
              "id": 1,
              "c": [],
              "t": "t",
              "at": "s",
              "p": [
                {
                  "l": "en_US",
                  "t": "What are you doing?"
                },
                {
                  "l": "it_IT",
                  "t": "Cosa stai facendo?"
                }
              ]
            },
            "a": [
              [
                {
                  "id": 1,
                  "c": [],
                  "c_id": -1,
                  "p": [
                    {
                      "l": "en_US",
                      "t": "I am working"
                    },
                    {
                      "l": "it_IT",
                      "t": "Sto lavorando"
                    }
                  ]
                },
                {
                  "id": 2,
                  "c": [],
                  "c_id": -1,
                  "p": [
                    {
                      "l": "en_US",
                      "t": "I am studying"
                    },
                    {
                      "l": "it_IT",
                      "t": "Sto studiando"
                    }
                  ]
                }
              ]
            ]
          },
          "day": 20190910,
          "instancetimestamp": 20190911201814344,
          "status": "success",
          "title": "Question Title"
        }
      ]
    }
  ]
}
"""


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
        parameters["from"] = date_from_str
        parameters["to"] = date_to_str
        parameters["properties"] = "locationeventpertime"
        for user in users:
            user_url = self._url + user
            self._users_locations[user] = None
            try:
                r = requests.get(
                    user_url,
                    params=parameters,
                    headers={
                        "Authorization": "test:wenet",
                        "Accept": "application/json",
                    },
                )
                if r.status_code == 200:
                    _LOGGER.debug(
                        f"request to stream base success for user {user} -  {r.json()}"
                    )
                    self._users_locations[
                        user
                    ] = self._gps_streambase_to_user_locations(r.json(), user)
                else:
                    _LOGGER.warn(
                        f"request to stream base failed for user {user} with code {r.status_code}"
                    )
            except RequestException as e:
                _LOGGER.warn(f"request to stream base failed for user {user} - {e}")
                _LOGGER.exception(e)

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
                try:
                    for obj in _property["locationeventpertime"]:
                        yield obj
                except KeyError:
                    continue

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
        try:
            return self._users_locations[user_id][:max_n]
        except KeyError:
            return []

    def get_locations_all_users(self, max_n=None):
        return [
            l for locations in self._users_locations.values() for l in locations[:max_n]
        ]


class StreambaseLabelsLoader(BaseSourceLabels):
    def __init__(self, location_loader, name="Streambase labels loader", last_days=14):
        super().__init__(name)
        self._location_loader = location_loader
        self._url = config.DEFAULT_STREAMBASE_BATCH_URL
        self._users_places = dict()
        self._users_staypoints = dict()
        self._users_stayregions = dict()
        for user in self.get_users():
            try:
                user_url = self._url + user
                surveys = self._load_survey(
                    user=user, url=user_url, last_days=last_days
                )
                locations = location_loader.get_locations(user)
                stay_points = estimate_stay_points(locations)
                stay_points = sorted(stay_points, key=lambda sp: sp._t_start)
                stay_regions = estimate_stay_regions(
                    stay_points, distance_threshold_m=20
                )
                self._users_staypoints[user] = stay_points
                self._users_stayregions[user] = stay_regions
                self._users_places[user] = self._load_user_places(
                    user, surveys, stay_regions
                )
            except:
                pass

    @staticmethod
    def _load_survey(user, url, last_days):
        parameters = dict()
        date_to = datetime.datetime.now()
        date_from = date_to - datetime.timedelta(hours=24 * last_days)
        date_to_str = date_to.strftime("%Y%m%d")
        date_from_str = date_from.strftime("%Y%m%d")
        survey_streambase = json.loads(SURVEY_STR_FAKE)
        # TODO change me to get token from partner?
        parameters["from"] = date_from_str
        parameters["to"] = date_to_str
        parameters["properties"] = "tasksanswers"
        try:
            r = requests.get(
                url,
                params=parameters,
                headers={"Authorization": "test:wenet", "Accept": "application/json"},
            )
            if r.status_code == 200:
                _LOGGER.debug(
                    f"request to stream base success for user {user} -  {r.json()}"
                )
                return r.json()
            else:
                _LOGGER.warn(
                    f"request to stream base failed for user {user} with code {r.status_code}"
                )
        except RequestException as e:
            _LOGGER.warn(f"request to stream base failed for user {user} - {e}")

        # TODO change me when survey onlines
        return survey_streambase

    @staticmethod
    def _load_user_places(user, surveys, staypoints):
        def _get_answers(surveys, answers_valid):
            properties = surveys["properties"]
            for _property in properties:
                for obj in _property["timediariesanswers"]:
                    answers = obj["answer"]
                    current_answer = ""
                    for answer in answers:
                        for a in answer:
                            if a["cnt"] in answers_valid:
                                current_answer = a["ctn"]
                    if current_answer != "":
                        yield current_answer, obj["answertimestamp"]

        answers_valid = set(["I am at home", "I am working", "I am studying"])
        user_places = []
        for label, timestamp in _get_answers(surveys, answers_valid):
            place = label
            try:
                pts_t = datetime.datetime.fromtimestamp(timestamp)
            except Exception as e:
                #  They dont use unix timestamp...
                # TODO change me when ppl respect unix timestamp...........
                _LOGGER.warn(
                    "invalid timestamp format from streambase surveys - will try to use anyway"
                )
                pts_t = datetime.datetime.strptime(str(timestamp)[:-3], "%Y%m%d%H%M%S")
            user_place_time_only = UserPlaceTimeOnly(pts_t, place, user)
            user_place = user_place_time_only.to_user_place_from_stay_points(staypoints)
            if user_place is not None:
                user_places.append(user_place)
        return user_places

    def get_users(self):
        return self._location_loader.get_users()

    def get_labels(self, user_id, max_n=None):
        try:
            return self._users_places[user_id][:max_n]
        except KeyError:
            return []

    def get_labels_all_users(self, max_n=None):
        return [
            user_place
            for sublist in self._users_places.values()
            for user_place in sublist
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
