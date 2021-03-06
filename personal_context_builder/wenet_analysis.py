"""
module that analyse user's routines

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,

"""
import json
import pickle
from copy import deepcopy
from datetime import datetime, timedelta
from functools import lru_cache
from os.path import join
from typing import Any, Callable, List, Optional
from uuid import uuid4

import numpy as np
import pandas as pd  # type: ignore
from regions_builder.algorithms import closest_locations  # type: ignore
from regions_builder.data_loading import MockWenetSourceLocations  # type: ignore
from regions_builder.models import GPSPoint  # type: ignore
from regions_builder.models import (
    LabelledStayRegion,
    LocationPoint,
    StayRegion,
    UserLocationPoint,
)
from scipy import spatial  # type: ignore

from personal_context_builder import config
from personal_context_builder.wenet_realtime_user_db import (
    DatabaseRealtimeLocationsHandler,
    DatabaseRealtimeLocationsHandlerMock,
)
from personal_context_builder.wenet_user_profile_db import (
    DatabaseProfileHandler,
    DatabaseProfileHandlerMock,
)


def compare_routines(
    source_user: str,
    users: List[str],
    model: Any,
    function: Callable = spatial.distance.cosine,
    is_mock: bool = False,
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
        db = DatabaseProfileHandlerMock.get_instance(db_index=model_num)
    else:
        db = DatabaseProfileHandler.get_instance(db_index=model_num)
    source_routine = db.get_profile(source_user)
    if source_routine is None:
        return dict()
    routines = [db.get_profile(u) for u in users]
    users, routines = zip(
        *[
            (user, routine)
            for (user, routine) in zip(users, routines)
            if routines is not None
        ]
    )
    routines_dist = [function(source_routine, r) for r in routines]
    res = list(zip(users, routines_dist))
    res = sorted(res, key=lambda x: -x[1])
    return dict(res)


def closest_users(lat: float, lng: float, N: int, is_mock: bool = False):
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
def _loads_regions(regions_mapping_file: str):
    """loads regions mapping file

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
        labelled_stay_regions: Optional[List[LabelledStayRegion]],
        stay_regions: Optional[List[StayRegion]],
        regions_mapping_file: str = config.PCB_REGION_MAPPING_FILE,
    ):
        if labelled_stay_regions is not None:
            self._labelled_stay_regions = labelled_stay_regions
        else:
            self._labelled_stay_regions = []
        if stay_regions is not None:
            self._stay_regions = stay_regions
        else:
            self._stay_regions = []
        self._regions_mapping = _loads_regions(regions_mapping_file)
        self._inner_vector_size = max(self._regions_mapping.values())

    @classmethod
    def group_by_days(
        cls,
        locations: List[LocationPoint],
        user: str = "unknown",
        start_day: str = "00:00:00",
        dt_hours: float = 23.5,
        freq: str = "30T",
    ):
        """class method to group the locations by days
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
            for row in df_day_activity.rename(
                columns={
                    "_pts_t": "pts_t",
                    "_user": "user",
                    "_lat": "lat",
                    "_lng": "lng",
                    "_accuracy_m": "accuracy_m",
                }
            ).itertuples():
                location = UserLocationPoint.from_namedtuple(row)
                current_day.append(location)
            days_list.append(current_day)
        return days_list

    def vectorize(self, locations: List[LocationPoint]):
        """Create a bag of words vector
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

    def save(
        self,
        filename: str = config.PCB_BOW_MODEL_FILE,
        dump_fct: Callable = pickle.dump,
    ):
        """save this current instance of BagOfWordsVectorizer
        Args:
            filename: file that will be used to store the instance
            dump_fct: function to use to dump the instance into a file
        """
        location = join(config.PCB_DATA_FOLDER, filename)
        with open(location, "wb") as f:
            dump_fct(self.__dict__, f)

    @staticmethod
    def load(
        filename: str = config.PCB_BOW_MODEL_FILE, load_fct: Callable = pickle.load
    ):
        """Create a instance of BagOfWordsVectorizer from a previously saved file
        Args:
            filename: file that contain the saved BagOfWordsVectorizer instance
            load_fct: function to use to load the instance from a file
        Return:
            An instance of BagOfWordsVectorizer
        """
        location = join(config.PCB_DATA_FOLDER, filename)
        with open(location, "rb") as f:
            instance = BagOfWordsVectorizer(None, None)
            instance.__dict__ = load_fct(f)
            return instance


class BagOfWordsCorpuzer(BagOfWordsVectorizer):
    def __init__(
        self,
        labelled_stay_regions: List[LabelledStayRegion],
        stay_regions: List[StayRegion],
        regions_mapping_file: str = config.PCB_REGION_MAPPING_FILE,
    ):
        super().__init__(
            labelled_stay_regions,
            stay_regions,
            regions_mapping_file=config.PCB_REGION_MAPPING_FILE,
        )

    def vectorize(self, locations: List[LocationPoint]):
        """Create a bag of words corpus
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
