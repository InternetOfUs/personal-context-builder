""" Module responsibles to communicate with Wenet profile manager, to fill the profiles with
    the routines
"""
from personal_context_builder import config
from regions_builder.data_loading import BaseSourceLocations, BaseSourceLabels
from regions_builder.models import LocationPoint, UserPlaceTimeOnly, UserLocationPoint
from regions_builder.algorithms import (
    estimate_stay_points,
    estimate_stay_regions,
    labelize_stay_region,
)
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


class StreamBaseLocationsLoader(BaseSourceLocations):
    def __init__(self, name="Streambase locations loader", last_days=24):
        super().__init__(name)

        users = self.get_latest_users()
        self._url = config.DEFAULT_STREAMBASE_BATCH_URL
        self._users_locations = dict()
        date_to = datetime.datetime.now()
        date_from = date_to - datetime.timedelta(hours=24 * last_days)
        self._users_locations = self.load_users_locations(users, date_from, date_to)

    @staticmethod
    def load_users_locations(
        users,
        date_from,
        date_to=None,
        url=config.DEFAULT_STREAMBASE_BATCH_URL,
    ):
        users_locations = dict()
        for user in users:
            locations = StreamBaseLocationsLoader.load_user_locations(
                user, date_from, date_to, url
            )
            if locations is not None:
                users_locations[user] = locations
        if len(users_locations) < 1:
            raise wenet_exceptions.WenetStreamBaseLocationsError()
        _LOGGER.info("StreamBase locations loaded")
        return users_locations

    @staticmethod
    def load_user_locations(
        user,
        date_from,
        date_to=None,
        url=config.DEFAULT_STREAMBASE_BATCH_URL,
    ):
        if date_to is None:
            date_to = datetime.datetime.now()
        date_to_str = date_to.strftime("%Y%m%d")
        date_from_str = date_from.strftime("%Y%m%d")
        parameters = dict()
        # TODO change me to get token from partner?
        parameters["from"] = date_from_str
        parameters["to"] = date_to_str
        parameters["properties"] = "locationeventpertime"
        parameters["userId"] = user
        user_url = url
        if config.DEFAULT_WENET_API_KEY == "":
            _LOGGER.warn(f"DEFAULT_WENET_API_KEY is empty")
        try:
            r = requests.get(
                user_url,
                params=parameters,
                headers={
                    "Authorization": "test:wenet",
                    "Accept": "application/json",
                    "x-wenet-component-apikey": config.DEFAULT_WENET_API_KEY,
                },
            )
            if r.status_code == 200:
                _LOGGER.debug(
                    f"request to stream base for locations success for user {user} -  {r.json()}"
                )
                return StreamBaseLocationsLoader._gps_streambase_to_user_locations(
                    r.json(), user
                )
            else:
                _LOGGER.warn(
                    f"request to stream base failed for user {user} with code {r.status_code} URL : {r.url}"
                )
        except RequestException as e:
            _LOGGER.warn(f"request to stream base failed for user {user} - {e}")
            _LOGGER.exception(e)

    @staticmethod
    def get_latest_users():
        url = (
            config.DEFAULT_PROFILE_MANAGER_URL
            + "/userIdentifiers?offset=0&limit=1000000"
        )
        try:
            if config.DEFAULT_WENET_API_KEY == "":
                _LOGGER.warn(f"DEFAULT_WENET_API_KEY is empty")
                res = requests.get(url)
            else:
                headers = {"x-wenet-component-apikey": config.DEFAULT_WENET_API_KEY}
                res = requests.get(url, headers=headers)
            res_json = res.json()
            return res_json["userIds"]
        except:
            _LOGGER.error(f"issue when requesting profile manager about IDs, code {res.status_code}, content {res.json()}")
            return ["0"]

    @staticmethod
    def _gps_streambase_to_user_locations(gps_streambase, user):
        def _get_only_gps_locations(gps_streambase):
            gps_streambase = gps_streambase[0]
            if "data" not in gps_streambase:
                _LOGGER.warn(f"no data for user {user} from streambase {gps_streambase}")
                return None
            data = gps_streambase["data"]
            locationeventpertime = data["locationeventpertime"]
            for _property in locationeventpertime:
                _property["payload"]["ts"] = _property["ts"]
                yield _property["payload"]

        locations = []
        locationeventpertime_list = _get_only_gps_locations(gps_streambase)
        for locationeventpertime in locationeventpertime_list:
            lat = locationeventpertime["point"]["latitude"]
            lng = locationeventpertime["point"]["longitude"]
            #  // 1000 because their ts is in milisec
            timestamp = locationeventpertime["ts"] // 1000
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
            user_url = self._url + user
            surveys = self._load_survey(user=user, url=user_url, last_days=last_days)
            if surveys is None:
                _LOGGER.debug(f"No surveys for user {user}")
                continue
            try:
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
            except ValueError as e:
                _LOGGER.debug(f"Can't load labels for user {user}")

    @staticmethod
    def _load_survey(user, url, last_days):
        parameters = dict()
        date_to = datetime.datetime.now()
        date_from = date_to - datetime.timedelta(hours=24 * last_days)
        date_to_str = date_to.strftime("%Y%m%d")
        date_from_str = date_from.strftime("%Y%m%d")
        # TODO change me to get token from partner?
        parameters["from"] = date_from_str
        parameters["to"] = date_to_str
        parameters["properties"] = "timediariesanswers"
        try:
            r = requests.get(
                url,
                params=parameters,
                headers={"Authorization": "test:wenet", "Accept": "application/json", "x-wenet-component-apikey": config.DEFAULT_WENET_API_KEY},
            )
            if r.status_code == 200:
                _LOGGER.debug(
                    f"request to stream base for labels success for user {user} -  {r.json()}"
                )
                return r.json()
            else:
                _LOGGER.warn(
                    f"request to stream base failed for user {user} with code {r.status_code}"
                )
        except RequestException as e:
            _LOGGER.warn(f"request to stream base failed for user {user} - {e}")

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
                                current_answer = a["cnt"]
                    if current_answer != "":
                        yield current_answer, obj["answertimestamp"]

        answers_valid = set(["Working (Paid)", "House"])
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


class Label(object):
    def __init__(self, name, semantic_class, latitude, longitude):
        self.name = name
        self.semantic_class = semantic_class
        self.latitude = latitude
        self.longitude = longitude

    def to_dict(self):
        return self.__dict__


class ScoredLabel(object):
    def __init__(self, score, label):
        self.label = label
        self.score = score

    def to_dict(self):
        return {"label": self.label, "score": self.score}


class PersonalBehavior(object):
    def __init__(self, user_id, weekday, confidence):
        self.user_id = user_id
        self.weekday = weekday
        self.confidence = confidence
        self.label_distribution = defaultdict(list)

    def fill(self, routine, labels):
        for timeslot, labels_distributions_dict in routine.items():
            timeslot_dist = []
            for label_id, score in labels_distributions_dict.items():
                if label_id == 0:
                    continue
                timeslot_dist.append(
                    ScoredLabel(score, labels[label_id].to_dict()).to_dict()
                )
            self.label_distribution[timeslot] = timeslot_dist

    def to_dict(self):
        my_dict = dict()
        my_dict["user_id"] = self.user_id
        my_dict["weekday"] = self.weekday
        my_dict["confidence"] = self.confidence
        my_dict["label_distribution"] = self.label_distribution
        return my_dict


def update_profiles():
    pass


def update_profile(routines, profile_id, url=config.DEFAULT_PROFILE_MANAGER_URL):
    profile_url = url + f"/profiles/{profile_id}"
    personal_behaviors = []
    labels = {1: Label("Working (Paid)", 1, 0, 0), 2: Label("House", 2, 0, 0)}

    for weekday, routine in routines.items():
        current_pb = PersonalBehavior(profile_id, weekday, 1)
        current_pb.fill(routine, labels)
        personal_behaviors.append(current_pb.to_dict())
    try:
        r = requests.patch(profile_url, data={"personalBehaviors": personal_behaviors}, headers={"x-wenet-component-apikey": config.DEFAULT_WENET_API_KEY})
        if r.status_code != 200:
            _LOGGER.warn(
                f"unable to update profile for user {profile_id} - status code {r.status_code}"
            )
        else:
            _LOGGER.debug(f"update profile for user {profile_id} success")
    except RequestException as e:
        _LOGGER.warn(f"unable to update profile for user {profile_id} - {e}")
        _LOGGER.exception(e)
