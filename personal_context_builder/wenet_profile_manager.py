""" Module responsibles to communicate with Wenet profile manager, to fill the profiles with
    the routines

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,

"""
import datetime
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from json import JSONDecodeError
from pprint import pprint
from time import sleep
from typing import Dict, List, Optional

import pandas as pd  # type: ignore
import requests  # type: ignore
from cachetools import LRUCache, TTLCache, cached  # type: ignore
from regions_builder.algorithms import estimate_stay_points  # type: ignore
from regions_builder.algorithms import estimate_stay_regions, labelize_stay_region
from regions_builder.data_loading import BaseSourceLabels  # type: ignore
from regions_builder.data_loading import BaseSourceLocations
from regions_builder.models import StayPoint  # type: ignore
from regions_builder.models import LocationPoint, UserLocationPoint, UserPlaceTimeOnly
from requests.exceptions import RequestException  # type: ignore

from personal_context_builder import config, wenet_exceptions
from personal_context_builder.wenet_logger import create_logger

_LOGGER = create_logger(__name__)


class StreamBaseLocationsLoader(BaseSourceLocations):
    def __init__(self, name: str = "Streambase locations loader", last_days: int = 24):
        super().__init__(name)

        users = self.get_latest_users()
        self._url = config.PCB_STREAMBASE_BATCH_URL
        self._users_locations = dict()
        date_to = datetime.datetime.now()
        date_from = date_to - datetime.timedelta(hours=24 * last_days)
        self._users_locations = self.load_users_locations(users, date_from, date_to)

    @staticmethod
    def load_users_locations(
        users: List[str],
        date_from: datetime.datetime,
        date_to: Optional[datetime.datetime] = None,
        url: str = config.PCB_STREAMBASE_BATCH_URL,
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
        user: str,
        date_from: datetime.datetime,
        date_to: Optional[datetime.datetime] = None,
        url: str = config.PCB_STREAMBASE_BATCH_URL,
        max_retry: int = 3,
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
        if config.PCB_WENET_API_KEY == "":
            _LOGGER.warn(f"PCB_WENET_API_KEY is empty")
        try:
            r = requests.get(
                user_url,
                params=parameters,
                headers={
                    "Authorization": "test:wenet",
                    "Accept": "application/json",
                    "x-wenet-component-apikey": config.PCB_WENET_API_KEY,
                },
            )
            if r.status_code == 200:
                try:
                    _LOGGER.debug(
                        f"request to stream base for locations success for user {user} -  {r.json()}"
                    )
                    return StreamBaseLocationsLoader._gps_streambase_to_user_locations(
                        r.json(), user
                    )
                except JSONDecodeError:
                    _LOGGER.warn(
                        f"locations json from stream base is not json {r.content}"
                    )
            else:
                _LOGGER.warn(
                    f"request to stream base failed for user {user} with code {r.status_code} URL : {r.url}"
                )
        except RequestException as e:
            _LOGGER.warn(f"request to stream base failed for user {user} - {e}")
            #  _LOGGER.exception(e)
        except TimeoutError as e:
            _LOGGER.warn(
                f"request to stream base failed for user {user} - {e} remaining retry {max_retry}"
            )
            #  _LOGGER.exception(e)
            if max_retry > 0:
                sleep(5)
                return StreamBaseLocationsLoader.load_user_locations(
                    user, date_from, date_to, url, max_retry - 1
                )
        except Exception as e:
            _LOGGER.warn(
                f"request to stream base failed for user {user} - {e} unhandle exception"
            )
            #  _LOGGER.exception(e)

    @staticmethod
    def get_latest_users():

        url = (
            config.PCB_PROFILE_MANAGER_URL
            + f"/userIdentifiers?offset={config.PCB_PROFILE_MANAGER_OFFSET}&limit={config.PCB_PROFILE_MANAGER_LIMIT}"
        )
        try:
            if config.PCB_WENET_API_KEY == "":
                _LOGGER.warn(f"PCB_WENET_API_KEY is empty")
                res = requests.get(url)
            else:
                headers = {"x-wenet-component-apikey": config.PCB_WENET_API_KEY}
                res = requests.get(url, headers=headers)
            res_json = res.json()
            return res_json["userIds"]
        except Exception as e:
            _LOGGER.error(f"issue when requesting profile manager users - {e}")
            _LOGGER.error(
                f"issue when requesting profile manager users - asked at {url}"
            )
            return ["0"]

    @staticmethod
    def _gps_streambase_to_user_locations(gps_streambase: List[Dict], user: str):
        def _get_only_gps_locations(gps_streambase):
            gps_streambase = gps_streambase[0]
            if "data" not in gps_streambase:
                _LOGGER.warn(
                    f"no data for user {user} from streambase {gps_streambase}"
                )
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
        if len(locations) > 0:
            locations = sorted(locations, key=lambda x: x._pts_t)
        return locations

    def get_users(self):
        return list(self._users_locations.keys())

    def get_locations(self, user_id: str, max_n: Optional[int] = None):
        try:
            return self._users_locations[user_id][:max_n]
        except KeyError:
            return []

    def get_locations_all_users(self, max_n: Optional[int] = None):
        return [
            l for locations in self._users_locations.values() for l in locations[:max_n]
        ]


class StreambaseLabelsLoader(BaseSourceLabels):
    def __init__(
        self,
        location_loader: BaseSourceLocations,
        name: str = "Streambase labels loader",
        last_days: int = 14,
    ):
        super().__init__(name)
        self._location_loader = location_loader
        self._url = config.PCB_STREAMBASE_BATCH_URL
        self._users_places = dict()
        self._users_staypoints = dict()
        self._users_stayregions = dict()
        for user in self.get_users():
            #  user_url = self._url + user
            user_url = self._url
            surveys = self._load_survey(user=user, url=user_url, last_days=last_days)
            if "timediariesanswers" not in str(surveys):
                surveys = None
            if surveys is None:
                _LOGGER.debug(f"No surveys for user {user}")
                continue
            _LOGGER.debug(f"Loaded {len(surveys)} surveys for user {user}")
            try:
                locations = location_loader.get_locations(user)
                _LOGGER.debug(f"{len(locations)} locations for user {user}")
                stay_points = estimate_stay_points(locations)
                _LOGGER.debug(f"{len(stay_points)} staypoints for user {user}")
                stay_points = sorted(stay_points, key=lambda sp: sp._t_start)
                stay_regions = estimate_stay_regions(
                    stay_points, distance_threshold_m=50
                )
                _LOGGER.debug(f"{len(stay_regions)} stay_regions for user {user}")
                self._users_staypoints[user] = stay_points
                self._users_stayregions[user] = stay_regions
                self._users_places[user] = self._load_user_places(
                    user, surveys, stay_regions
                )
            except ValueError as e:
                _LOGGER.debug(f"Can't load labels for user {user}")

    @staticmethod
    def _load_survey(user: str, url: str, last_days: int):
        parameters = dict()
        date_to = datetime.datetime.now()
        date_from = date_to - datetime.timedelta(hours=24 * last_days * 100)
        date_to_str = date_to.strftime("%Y%m%d")
        date_from_str = date_from.strftime("%Y%m%d")
        # TODO change me to get token from partner?
        parameters["from"] = date_from_str
        parameters["to"] = date_to_str
        parameters["properties"] = "timediariesanswers"
        parameters["userId"] = user
        try:
            r = requests.get(
                url,
                params=parameters,
                headers={
                    "Authorization": "test:wenet",
                    "Accept": "application/json",
                    "x-wenet-component-apikey": config.PCB_WENET_API_KEY,
                },
            )
            if r.status_code == 200:
                try:
                    _LOGGER.debug(
                        f"request to stream base for labels success for user {user}"
                    )
                    return r.json()
                except JSONDecodeError:
                    _LOGGER.warn(
                        f"labels json from stream base is not json {r.content}"
                    )
            else:
                _LOGGER.warn(
                    f"request to stream base labels failed for user {user} with code {r.status_code} url {r.url}"
                )
        except RequestException as e:
            _LOGGER.warn(f"request to stream base labels failed for user {user} - {e}")

    @staticmethod
    def _load_user_places(user: str, surveys: Dict, staypoints: List[StayPoint]):
        def _get_answers(surveys):
            data = surveys["data"]
            taskanswers = data["timediariesanswers"]
            for taskanswer in taskanswers:
                payload = taskanswer["payload"]
                answer = payload["answer"]
                timestamp = payload["answertimestamp"]
                if answer is not None:
                    yield answer[0][0]["cnt"], timestamp

        user_places = []
        surveys = surveys[0]
        for label, timestamp in _get_answers(surveys):
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

    def get_labels(self, user_id: str, max_n: Optional[int] = None):
        try:
            return self._users_places[user_id][:max_n]
        except KeyError:
            return []

    def get_labels_all_users(self, max_n: Optional[int] = None):
        return [
            user_place
            for sublist in self._users_places.values()
            for user_place in sublist
        ]


class Label(object):
    def __init__(
        self, name: str, semantic_class: int, latitude: float, longitude: float
    ):
        self.name = name
        self.semantic_class = semantic_class
        self.latitude = latitude
        self.longitude = longitude

    def to_dict(self):
        return self.__dict__


class ScoredLabel(object):
    def __init__(self, score: float, label: str):
        self.label = label
        self.score = score

    def to_dict(self):
        return {"label": self.label, "score": self.score}


class PersonalBehavior(object):
    def __init__(self, user_id: str, weekday: int, confidence: float):
        self.user_id = user_id
        self.weekday = weekday
        self.confidence = confidence
        self.label_distribution: Dict[str, List[Dict[int, float]]] = defaultdict(list)

    def fill(self, routine: Dict[str, Dict[int, float]], labels: Dict):
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
        my_dict["weekday"] = str(self.weekday)
        my_dict["confidence"] = self.confidence
        my_dict["label_distribution"] = dict(
            [(ts, dist) for ts, dist in self.label_distribution.items() if dist != []]
        )
        return my_dict


@dataclass
class RelevantLocation(object):
    label: str
    latitude: float
    longitude: float


def update_profiles():
    pass


def update_profile(
    routines: Dict[int, Dict[str, Dict[int, float]]],
    profile_id: str,
    labels: Dict,
    url: str = config.PCB_PROFILE_MANAGER_URL,
):
    profile_url = url + f"/profiles/{profile_id}"
    personal_behaviors = []

    for weekday, routine in routines.items():
        current_pb = PersonalBehavior(profile_id, weekday, 1)
        current_pb.fill(routine, labels)
        personal_behaviors.append(current_pb.to_dict())
    try:
        r = requests.patch(
            profile_url,
            json={"personalBehaviors": personal_behaviors},
            headers={
                "x-wenet-component-apikey": config.PCB_WENET_API_KEY,
                "Content-Type": "application/json",
            },
        )
        if r.status_code != 200:
            _LOGGER.warn(
                f"unable to update profile for user {profile_id} - status code {r.status_code}"
            )
            _LOGGER.debug(
                f"content for {profile_id} is {r.content} from {r.request.body}"
            )
        else:
            _LOGGER.debug(f"update profile for user {profile_id} success")
    except RequestException as e:
        _LOGGER.warn(f"unable to update profile for user {profile_id} - {e}")


def update_profile_relevant_locations(
    labelled_stayregions: List,
    profile_id: str,
    url: str = config.PCB_PROFILE_MANAGER_URL,
):
    profile_url = url + f"/profiles/{profile_id}"
    relevant_locations = []

    for labelled_stayregion in labelled_stayregions:
        latitude = (
            labelled_stayregion._topleft_lat + labelled_stayregion._bottomright_lat
        ) / 2
        longitude = (
            labelled_stayregion._topleft_lng + labelled_stayregion._bottomright_lng
        ) / 2
        label = labelled_stayregion._label
        current_rl = RelevantLocation(
            label=label, latitude=latitude, longitude=longitude
        )
        relevant_locations.append(asdict(current_rl))
    try:
        r = requests.patch(
            profile_url,
            json={"RelevantLocations": relevant_locations},
            headers={
                "x-wenet-component-apikey": config.PCB_WENET_API_KEY,
                "Content-Type": "application/json",
            },
        )
        if r.status_code != 200:
            _LOGGER.warn(
                f"unable to update relevantLocations in profile for user {profile_id} - status code {r.status_code}"
            )
            _LOGGER.debug(
                f"content for {profile_id} is {r.content} from {r.request.body}"
            )
        else:
            _LOGGER.debug(f"update profile for user {profile_id} success")
    except RequestException as e:
        _LOGGER.warn(f"unable to update profile for user {profile_id} - {e}")


@cached(cache=TTLCache(maxsize=None, ttl=600))
def update_profile_has_locations(
    profile_id: str,
    url: str = config.PCB_PROFILE_MANAGER_URL,
):
    # don't patch empty users
    if profile_id is None or profile_id == "":
        _LOGGER.warn("update_profile_has_locations profile_id was empty")
        return
    profile_url = url + f"/profiles/{profile_id}"
    try:
        r = requests.patch(
            profile_url,
            json={"hasLocations": True},
            headers={
                "x-wenet-component-apikey": config.PCB_WENET_API_KEY,
                "Content-Type": "application/json",
            },
        )
        if r.status_code != 200:
            _LOGGER.warn(
                f"unable to update profile (has_locations) for user {profile_id} - status code {r.status_code}"
            )
            _LOGGER.debug(
                f"content for {profile_id} is {r.content} from {r.request.body}"
            )
        else:
            _LOGGER.debug(
                f"update profile (has_locations) for user {profile_id} success"
            )
    except RequestException as e:
        _LOGGER.warn(
            f"unable to update profile (has_locations) for user {profile_id} - {e}"
        )
    except Exception as e:
        _LOGGER.warn(
            f"unable to update profile (has_locations) for user {profile_id} - {e}"
        )
