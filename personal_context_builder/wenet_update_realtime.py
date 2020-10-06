""" module that update the real-time service

"""
import concurrent.futures
from personal_context_builder.wenet_profile_manager import StreamBaseLocationsLoader
from personal_context_builder import config


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
            "timestamp": timestamp,
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy,
        }

    def get_user_location(self, user_id):
        date_to = datetime.datetime.now()
        date_from = date_to - datetime.timedelta(minutes=5)
        res = StreamBaseLocationsLoader.load_user_locations(user=user_id)
        if res is not None:
            return res[-1]

    def get_all_users(self):
        return StreamBaseLocationsLoader.get_latest_users()