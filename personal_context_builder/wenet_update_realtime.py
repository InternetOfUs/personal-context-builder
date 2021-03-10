""" module that update the real-time service

"""
import concurrent.futures
from datetime import datetime, timedelta
from personal_context_builder.wenet_profile_manager import StreamBaseLocationsLoader
from personal_context_builder import config
import requests


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
            f"http://{config.DEFAULT_REALTIME_HOST}:{config.DEFAULT_REALTIME_PORT}/users_locations/",
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
