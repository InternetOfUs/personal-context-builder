""" module that update the real-time service

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,


"""
import concurrent.futures
from datetime import datetime, timedelta
from functools import partial
from multiprocessing.pool import ThreadPool
from random import shuffle
from time import sleep
from typing import Iterable, List, Optional, Tuple, Union

import requests  # type: ignore
import urllib3  # type: ignore
from regions_builder.models import LocationPoint, UserLocationPoint  # type: ignore
from requests.exceptions import RequestException  # type: ignore

from personal_context_builder import config
from personal_context_builder.wenet_logger import create_logger
from personal_context_builder.wenet_profile_manager import (
    StreamBaseLocationsLoader,
    update_profile_has_locations,
)

_LOGGER = create_logger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def batch(my_list: List[str], n: int = 1) -> Iterable[List[str]]:
    my_len = len(my_list)
    for ndx in range(0, my_len, n):
        yield my_list[ndx : ndx + n]


class WenetRealTimeUpdateHandler(object):
    """class that handle the updating of the realtime component"""

    def __init__(self):
        pass

    @staticmethod
    def update_user_location(
        user_id: str,
        timestamp: Union[int, str],
        latitude: float,
        longitude: float,
        accuracy: int = 0,
        max_retry: int = 5,
    ):
        """update the user location

        Args:
            user_id: user to update
            timestamp: timestamp of the recorded data
            latitude: latitude
            longitude: longitude
            accuracy: accuracy
        """
        my_dict = {
            "id": user_id,
            "timestamp": int(timestamp),
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": int(accuracy),
        }
        try:
            requests.post(f"{config.PCB_USER_LOCATION_URL}", json=my_dict, verify=False)
        except RequestException as e:
            _LOGGER.warn(f"request to update realtime for user {user_id} - {e}")
        except TimeoutError as e:
            _LOGGER.warn(
                f"request to update realtime for use {user_id} - {e} remaining retry {max_retry}"
            )
            if max_retry > 0:
                sleep(5)
                return WenetRealTimeUpdateHandler.update_user_location(
                    user_id, timestamp, latitude, longitude, accuracy, max_retry - 1
                )
        except Exception as e:
            _LOGGER.warn(
                f"request to update realtime for use {user_id} - {e} unhandle exception"
            )

    @staticmethod
    def get_user_location(user_id: str) -> Optional[UserLocationPoint]:
        """Retreive the location of the given user

        Args:
            user_id: user to retrieve

        Return: The latest location if available
        """
        date_to = datetime.now()
        date_from = date_to - timedelta(minutes=5)

        #  TODO solve issue with time and localtime differences
        date_to = date_to + timedelta(minutes=120)

        res = StreamBaseLocationsLoader.load_user_locations(
            user=user_id, date_from=date_from, date_to=date_to
        )
        if res is not None and len(res) > 0:
            return res[-1]
        else:
            return None

    def get_all_users(self) -> List[UserLocationPoint]:
        """get all users"""
        return StreamBaseLocationsLoader.get_latest_users()

    @staticmethod
    def run_one_user(user_location: Tuple[str, Optional[LocationPoint]]):
        try:
            user, location = user_location
            if location is not None:
                timestamp = int(datetime.timestamp(location._pts_t))
                WenetRealTimeUpdateHandler.update_user_location(
                    user,
                    timestamp=timestamp,
                    latitude=location._lat,
                    longitude=location._lng,
                )
                if config.PCB_PROFILE_MANAGER_UPDATE_HAS_LOCATIONS:
                    update_profile_has_locations(user)
        except Exception as e:
            f"unknown error run_one_user - {e} unhandle exception"

    def run_once(self):
        """retreive and update the locations of all users"""
        users = self.get_all_users()
        shuffle(users)
        _LOGGER.info(f"start to update {len(users)} users")
        for users_batch in batch(users, 500):
            _LOGGER.info(f"start to update batch of {len(users_batch)} users")
            with ThreadPool(min(100, len(users_batch))) as pool:
                locations = list(
                    pool.map(WenetRealTimeUpdateHandler.get_user_location, users_batch)
                )
                users_location = zip(users_batch, locations)
                pool.map(WenetRealTimeUpdateHandler.run_one_user, users_location)
            pool.join()
            _LOGGER.info(f"{len(users_batch)} users updated")
        _LOGGER.info(f"{len(users)} users updated")
