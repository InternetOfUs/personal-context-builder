"""
Module to train a new models to create user's profiles

This is a quick & dirty script for testing. The proper wenet data will be used by using proper API
"""

from glob import glob
import re
from copy import deepcopy
from functools import partial
from datetime import datetime, timedelta
from collections import defaultdict
from progress.bar import Bar
import pandas as pd
import numpy as np
from personal_context_builder.wenet_models import LocationPoint, UserPlaceTimeOnly
from personal_context_builder.wenet_algo import (
    estimate_stay_points,
    estimate_stay_regions,
    labelize_stay_region,
)
from personal_context_builder.wenet_tools import time_difference_ms
from personal_context_builder.wenet_analysis import BagOfWordsVectorizer
from personal_context_builder.wenet_analysis_models import BaseModelWrapper
from sklearn.decomposition import LatentDirichletAllocation
import pickle


def get_locations_from_df_without_time(df):
    locations = []
    for index, row in df.iterrows():
        try:
            accuracy = row["accuracy"]
            pts_t = None
            location = LocationPoint(pts_t, row["latitude"], row["longitude"], accuracy)
            locations.append(location)
        except ValueError:
            locations.append(None)
    return locations


def get_locations_from_df(df):
    locations = []
    for index, row in df.iterrows():
        try:
            accuracy = row["accuracy"]
            pts_t = datetime.fromtimestamp(row["timestamp"])
            location = LocationPoint(pts_t, row["latitude"], row["longitude"], accuracy)
            locations.append(location)
        except ValueError:
            locations.append(None)
    return locations


def get_labelled_stay_regions(df, stay_regions, user, stay_points):
    """TODO use stay_regions_set instead of stay regions"""
    user_places = []
    for index, row in df.iterrows():
        pts_t = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
        if row["place_type"] == "personal":
            place = row["place_id_name"]
        else:
            place = row["place_type"]
        user_place_time_only = UserPlaceTimeOnly(pts_t, place, user)
        user_place = user_place_time_only.to_user_place_from_stay_points(
            stay_points, max_delta_time_ms=1000 * 60 * 3
        )
        if user_place is not None:
            user_places.append(user_place)
    labelled_stay_regions = labelize_stay_region(stay_regions, user_places)
    stay_regions_set = set(stay_regions) - labelled_stay_regions
    return labelled_stay_regions


def create_df_all():
    locations_glob_expr = "/idiap/temp/wdroz/locations/*.csv"
    all_location_files = glob(locations_glob_expr)
    user_regex = re.compile(r"\/([^/\\_]+)_location\.csv")
    df_list = []
    users_list = []
    bar = Bar("processing location files", max=len(all_location_files))
    for location_file in all_location_files:
        bar.next()
        df = pd.read_csv(location_file)
        df["date"] = pd.to_datetime(df["timestamp"] + df["timezone"], unit="s")
        df = df.set_index("date")
        df = df[~df.index.duplicated(keep="first")]
        current_user = re.search(user_regex, location_file).group(1)
        users_list.append(current_user)
        df_list.append(df)
    bar.finish()
    df_all = pd.concat(df_list)
    return df_all, users_list


def get_users_stay_regions(users_list, df_all, df_ambiance):
    users_labelled_stay_regions = dict()
    users_stay_regions = dict()
    for user in users_list:
        df_user_locations = df_all[df_all["userid"] == user]
        user_locations = get_locations_from_df(df_user_locations)
        stay_points = estimate_stay_points(user_locations)
        if len(stay_points) < 1:
            continue
        df_user_ambiance = df_ambiance[df_ambiance["user"] == user]
        stay_regions = estimate_stay_regions(stay_points, distance_threshold_m=20)
        labelled_stay_regions = get_labelled_stay_regions(
            df_user_ambiance, stay_regions, user, stay_points
        )
        users_stay_regions[user] = stay_regions
        users_labelled_stay_regions[user] = labelled_stay_regions
    return users_stay_regions, users_labelled_stay_regions


def create_user_night_activities(df_all, users_labelled_stay_regions):
    user_night_activities = defaultdict(dict)
    users_vectorizer = dict()
    for name, grouped in df_all.groupby("night"):
        for user in users_labelled_stay_regions.keys():
            df_user_night = grouped[grouped["userid"] == user]
            night = str(name)
            year = night[:4]
            month = night[4:6]
            days = night[6:]
            start_date = datetime.strptime(
                f"{year}-{month}-{days} 20:00:00", "%Y-%m-%d %H:%M:%S"
            )
            end_date = start_date + timedelta(hours=8)
            df_median = df_user_night.resample("30T").median()
            df_user_activity = df_median.reindex(
                pd.date_range(start=start_date, end=end_date, freq="30T")
            )
            if user not in users_vectorizer:
                labelled_stay_regions = users_labelled_stay_regions[user]
                stay_regions = users_stay_regions[user]
                bow_user = BagOfWordsVectorizer(
                    labelled_stay_regions, stay_regions, "yn/yn_regions_mapping.json"
                )
                users_vectorizer[user] = bow_user
            locations = get_locations_from_df_without_time(df_user_activity)
            activity_vector = users_vectorizer[user].vectorize(locations)
            user_night_activities[user][str(night)] = activity_vector
    return user_night_activities


if __name__ == "__main__":
    df_ambiance = pd.read_csv(
        "/idiap/temp/wdroz/wenet/surveys/ambiance_survey.csv",
        sep=",",
        encoding="ISO-8859-1",
    )
    df_all, users_list = create_df_all()
    print(f"number of elements in df_all : {len(df_all)}")
    print(f"number of elements in users_list : {len(users_list)}")

    users_stay_regions, users_labelled_stay_regions = get_users_stay_regions(
        users_list, df_all, df_ambiance
    )
    print(f"number of elements in users_stay_regions : {len(users_stay_regions)}")
    print(
        f"number of elements in users_labelled_stay_regions : {len(users_labelled_stay_regions)}"
    )
    user_night_activities = create_user_night_activities(
        df_all, users_labelled_stay_regions
    )
    file_user_night_activities = "/idiap/temp/wdroz/wenet/yn_user_night_activities.p"
    print("saving user_night_activities")
    with open(file_user_night_activities, "wb") as f:
        pickle.dump(user_night_activities, f)
    print(f"number of elements in user_night_activities : {len(user_night_activities)}")
    X = [
        v
        for user, nights in user_night_activities.items()
        for night, v in nights.items()
    ]
    my_lda = partial(
        LatentDirichletAllocation, n_components=15, random_state=0, n_jobs=-1
    )
    my_model = BaseModelWrapper(my_lda, "lda YN")
    print(f"training model {my_model._name}")
    my_model.fit(X)
    model_name = "yn_model.p"
    print(f"saving model {model_name}")
    my_model.save(model_name)
