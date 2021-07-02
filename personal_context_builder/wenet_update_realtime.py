""" module that update the real-time service

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,


"""
import concurrent.futures
from datetime import datetime, timedelta

import requests

from personal_context_builder import config
from personal_context_builder.wenet_profile_manager import StreamBaseLocationsLoader


class WenetRealTimeUpdateHandler(object):
    def __init__(self):
        pass

    def update_user_location(
        self,
        user_id,
        timestamp,
        latitude,
        longitude,
        accuracy=0,
    ):
        my_dict = {
            "id": user_id,
            "timestamp": int(timestamp),
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": int(accuracy),
        }
        requests.post(
            f"{config.DEFAULT_USER_LOCATION_URL}",
            json=my_dict,
        )

    def get_user_location(self, user_id):
        date_to = datetime.now()
        date_from = date_to - timedelta(minutes=5)

        #  TODO solve issue with time and localtime differences
        date_to = date_to + timedelta(minutes=120)

        res = StreamBaseLocationsLoader.load_user_locations(
            user=user_id, date_from=date_from, date_to=date_to
        )
        if res is not None and len(res) > 0:
            return res[-1]

    def get_all_users(self):
        return StreamBaseLocationsLoader.get_latest_users()

    def run_once(self):
        # TODO use async
        # https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor-example
        users = self.get_all_users()
        for user in users:
            location = self.get_user_location(user)
            if location is not None:
                timestamp = datetime.timestamp(location._pts_t)
                self.update_user_location(
                    user,
                    timestamp=timestamp,
                    latitude=location._lat,
                    longitude=location._lng,
                )
