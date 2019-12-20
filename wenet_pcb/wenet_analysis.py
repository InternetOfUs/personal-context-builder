"""
module that analyse user's routines
"""
from wenet_pcb import config
import json
from uuid import uuid4
import numpy as np
from copy import deepcopy
from os.path import join
from functools import lru_cache
import pickle
import pandas as pd
from datetime import datetime, timedelta
from regions_builder.models import UserLocationPoint
from regions_builder.algorithms import closest_locations
from wenet_pcb.wenet_realtime_user_db import (
    DatabaseRealtimeLocationsHandlerMock,
    DatabaseRealtimeLocationsHandler,
)
from wenet_pcb.wenet_user_profile_db import (
    DatabaseProfileHandler,
    DatabaseProfileHandlerMock,
)
from regions_builder.models import GPSPoint
from wenet_pcb.wenet_data_loading import MockWenetSourceLocations
from scipy import spatial


def compare_routines(
    source_user, users, model, function=spatial.distance.cosine, is_mock=False
):
    """
    compare routines of users
    Args:
        source_user: the user that will be compared to the users
        users: list of users to compare to
        model: on which model the comparison should be applied
        function: the similarity function to use
        is_mock: if true, use mocked data
    """
    model_num = config.MAP_MODEL_TO_DB[model]
    if is_mock:
        db = DatabaseProfileHandlerMock.get_instance(model_num)
    else:
        db = DatabaseProfileHandler.get_instance(model_num)
    source_routine = db.get_profile(source_user)
    routines = [db.get_profile(u) for u in users]
    routines_dist = [function(source_routine, r) for r in routines]
    res = list(zip(users, routines_dist))
    res = sorted(res, key=lambda x: -x[1])
    return dict(res)


def closest_users(lat, lng, N, is_mock=False):
    """
    give the N closest users to the point (lat, lng)
    Args:
        lat: the latitude
        lng: the longitude
        N: how many users in output
        is_mock: if true, use mocked data
    """
    point = GPSPoint(lat, lng)
    if is_mock:
        db = DatabaseRealtimeLocationsHandlerMock.get_instance()
        fake_locations = [
            MockWenetSourceLocations._create_fake_locations(str(uuid4()), nb=1)[0]
            for _ in range(3000)
        ]
        db.update(fake_locations)
    else:
        db = DatabaseRealtimeLocationsHandler.get_instance()
    users_locations = db.get_all_users().values()
    sorted_users_locations = closest_locations(point, users_locations, N=N)
    return sorted_users_locations


@lru_cache(maxsize=None)
def _loads_regions(regions_mapping_file):
    """ loads regions mapping file

    this function is cached to avoid unnecessary disk accesses

    Args:
        regions_mapping_file: the filename where the json mapping file is

    Return:
        dict created from the json file
    """
    with open(regions_mapping_file, "r") as f:
        return json.load(f)


class BagOfWordsVectorizer(object):
    def __init__(
        self,
        labelled_stay_regions,
        stay_regions,
        regions_mapping_file=config.DEFAULT_REGION_MAPPING_FILE,
    ):
        self._labelled_stay_regions = labelled_stay_regions
        self._stay_regions = stay_regions
        self._regions_mapping = _loads_regions(regions_mapping_file)
        self._inner_vector_size = max(self._regions_mapping.values())

    @classmethod
    def group_by_days(
        cls, locations, user="unknown", start_day="00:00:00", dt_hours=23.5, freq="30T"
    ):
        """ class method to group the locations by days
        Args:
            locations: list of location to use
            user: user to use to create UserLocationPoint
            start_day: "HH:MM:SS" to define the start of a day
            dt_hours: how many hours we use from the start_day to define the day
            freq: at which freqency the data will be sample
        Return:
            List of list of location, each sublist is a day
        """
        data = [l.__dict__ for l in locations]
        df = pd.DataFrame.from_records(data)
        df["_pts_t"] = pd.to_datetime(df["_pts_t"])
        df["days"] = df["_pts_t"].dt.strftime("%Y%m%d")
        df["index"] = df["_pts_t"]
        df = df.set_index("index")
        days_list = []
        for name, grouped in df.groupby("days"):
            current_day = []
            fullday = str(name)
            year = fullday[:4]
            month = fullday[4:6]
            days = fullday[6:]
            start_date = datetime.strptime(
                f"{year}-{month}-{days} {start_day}", "%Y-%m-%d %H:%M:%S"
            )
            end_date = start_date + timedelta(hours=dt_hours)
            df_median = grouped.resample(freq).median()
            df_day_activity = df_median.reindex(
                pd.date_range(start=start_date, end=end_date, freq=freq)
            )
            df_day_activity["_pts_t"] = df_day_activity.index
            df_day_activity["_user"] = [user for _ in range(len(df_day_activity))]
            for index, row in df_day_activity.iterrows():
                location = UserLocationPoint.from_dict(row)
                current_day.append(location)
            days_list.append(current_day)
        return days_list

    def vectorize(self, locations):
        """ Create a bag of words vector
        Args:
            locations: list of LocationPoint

        Return:
            vector (list of floats)
        """
        big_vector = []
        inner_vector = [0] * self._inner_vector_size
        for location in locations:
            current_vector = deepcopy(inner_vector)
            if location is None or np.isnan(location._lat):
                current_vector[self._regions_mapping["no_data"]] = 1
            else:
                is_in_region = False
                for region in self._labelled_stay_regions:
                    if location in region:
                        if region._label in self._regions_mapping:
                            label = self._regions_mapping[region._label]
                        else:
                            label = self._regions_mapping["unknown_labelled_region"]
                        current_vector[label] = 1
                        is_in_region = True
                        break
                for region in self._stay_regions:
                    if location in region:
                        current_vector[self._regions_mapping["unknown_region"]] = 1
                        is_in_region = True
                        break
                if not is_in_region:
                    current_vector[self._regions_mapping["unknown"]] = 1
            big_vector += current_vector
        return big_vector

    def save(self, filename=config.DEFAULT_BOW_MODEL_FILE, dump_fct=pickle.dump):
        """ save this current instance of BagOfWordsVectorizer
            Args:
                filename: file that will be used to store the instance
                dump_fct: function to use to dump the instance into a file
        """
        location = join(config.DEFAULT_DATA_FOLDER, filename)
        with open(location, "wb") as f:
            dump_fct(self.__dict__, f)

    @staticmethod
    def load(filename=config.DEFAULT_BOW_MODEL_FILE, load_fct=pickle.load):
        """ Create a instance of BagOfWordsVectorizer from a previously saved file
            Args:
                filename: file that contain the saved BagOfWordsVectorizer instance
                load_fct: function to use to load the instance from a file
            Return:
                An instance of BagOfWordsVectorizer
        """
        location = join(config.DEFAULT_DATA_FOLDER, filename)
        with open(location, "rb") as f:
            instance = BagOfWordsVectorizer(None, None)
            instance.__dict__ = load_fct(f)
            return instance


class BagOfWordsCorpuzer(BagOfWordsVectorizer):
    def __init__(
        self,
        labelled_stay_regions,
        stay_regions,
        regions_mapping_file=config.DEFAULT_REGION_MAPPING_FILE,
    ):
        super().__init__(
            labelled_stay_regions,
            stay_regions,
            regions_mapping_file=config.DEFAULT_REGION_MAPPING_FILE,
        )

    def vectorize(self, locations):
        """ Create a bag of words corpus
        Args:
            locations: list of LocationPoint

        Return:
            list of list of "word"
        """
        big_vector = []
        for location in locations:
            inner_vector = []
            if location is None or np.isnan(location._lat):
                inner_vector.append(str(self._regions_mapping["no_data"]))
            else:
                is_in_region = False
                for region in self._labelled_stay_regions:
                    if location in region:
                        if region._label in self._regions_mapping:
                            label = self._regions_mapping[region._label]
                        else:
                            label = self._regions_mapping["unknown_labelled_region"]
                        inner_vector.append(str(label))
                        is_in_region = True
                        break
                for region in self._stay_regions:
                    if location in region:
                        inner_vector.append(
                            str(self._regions_mapping["unknown_region"])
                        )
                        is_in_region = True
                        break
                if not is_in_region:
                    inner_vector.append(str(self._regions_mapping["unknown"]))
            big_vector.append(inner_vector)
        return big_vector

