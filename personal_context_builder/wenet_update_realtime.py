""" module that update the real-time service

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,


"""
import concurrent.futures
from datetime import datetime, timedelta
from functools import partial
from multiprocessing.pool import ThreadPool
from typing import List, Optional, Tuple, Union

import requests  # type: ignore
import urllib3  # type: ignore
from regions_builder.models import LocationPoint, UserLocationPoint  # type: ignore

from personal_context_builder import config
from personal_context_builder.wenet_logger import create_logger
from personal_context_builder.wenet_profile_manager import StreamBaseLocationsLoader

_LOGGER = create_logger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
        requests.post(f"{config.PCB_USER_LOCATION_URL}", json=my_dict, verify=False)

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
        user, location = user_location
        if location is not None:
            timestamp = int(datetime.timestamp(location._pts_t))
            WenetRealTimeUpdateHandler.update_user_location(
                user,
                timestamp=timestamp,
                latitude=location._lat,
                longitude=location._lng,
            )

    def run_once(self):
        """retreive and update the locations of all users"""
        users = self.get_all_users()
        _LOGGER.info(f"start to update {len(users)} users")
        with ThreadPool(min(150, len(users))) as pool:
            locations = list(
                pool.map(WenetRealTimeUpdateHandler.get_user_location, users)
            )
            users_location = zip(users, locations)
            pool.map(WenetRealTimeUpdateHandler.run_one_user, users_location)
        pool.join()
        _LOGGER.info(f"{len(users)} users updated")
