""" Loading data from YN
"""

from glob import glob
import re
from datetime import datetime

import pandas as pd

from wenet_models import UserLocationPoint, UserPlaceTimeOnly
from wenet_data_loading import BaseSourceLabels, BaseSourceLocations


class YNSourceLocations(BaseSourceLocations):
    def __init__(self, name):
        super().__init__(name)

    def get_users(self):
        users = []
        locations_glob_expr = "/idiap/temp/wdroz/locations/*.csv"
        all_location_files = glob(locations_glob_expr)
        user_regex = re.compile(r"\/([^/\\_]+)_location\.csv")
        for location_file in all_location_files:
            current_user = re.search(user_regex, location_file).group(1)
            users.append(current_user)
        return users

    def get_locations(self, user_id, max_n=None):
        location_file = f"/idiap/temp/wdroz/locations/{user_id}_location.csv"
        df = pd.read_csv(location_file)
        df["date"] = pd.to_datetime(df["timestamp"] + df["timezone"], unit="s")
        df = df.set_index("date")
        df = df[~df.index.duplicated(keep="first")]
        locations = []
        for index, row in df.iterrows():
            try:
                accuracy = row["accuracy"]
                pts_t = datetime.fromtimestamp(row["timestamp"])
                location = UserLocationPoint(
                    pts_t, row["latitude"], row["longitude"], accuracy, user_id
                )
                locations.append(location)
            except ValueError:
                locations.append(None)
        return locations[:max_n]

    def get_locations_all_users(self, max_n=None):
        users_dict = dict()
        for user in self.get_users():
            users_dict[user] = self.get_locations(user, max_n=max_n)
        return users_dict


class YNSourceLabels(BaseSourceLabels):
    def __init__(self, name):
        super().__init__(name)
        self._df_ambiance = pd.read_csv(
            "/idiap/temp/wdroz/wenet/surveys/ambiance_survey.csv",
            sep=",",
            encoding="ISO-8859-1",
        )
        self._yn_source_locations = YNSourceLocations("yn locations")

    def get_users(self):
        return list(set(self._df_ambiance["user"].tolist()))

    def get_labels(self, user_id, max_n=None):
        locations = self._yn_source_locations.get_locations(user_id)
        if len(locations) == 0:
            return []
        user_places = []
        df_user = self._df_ambiance[self._df_ambiance["user"] == user_id]
        for index, row in df_user.iterrows():
            pts_t = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if row["place_type"] == "personal":
                place = row["place_id_name"]
            else:
                place = row["place_type"]
            user_place_time_only = UserPlaceTimeOnly(pts_t, place, user_id)
            user_place = user_place_time_only.to_user_place(locations)
            if user_place is not None:
                user_places.append(user_place)
        return user_places

    def get_labels_all_users(self, max_n=None):
        users_dict = dict()
        for user in self.get_users():
            users_dict[user] = self.get_labels(user, max_n=max_n)
        return users_dict