"""
module that work with Y@N data
"""
import argparse
import json
from collections import defaultdict
from datetime import datetime
from glob import glob
from os.path import join

import pandas as pd
from progress.bar import Bar

from personal_context_builder.wenet_algo import get_label_if_exist
from personal_context_builder.wenet_models import LocationPoint, UserPlaceTimeOnly
from yn.yn_algo import yn_estimate_stay_points, yn_estimate_stay_regions
from yn.yn_models import YNLocationPoint, YNUser


def get_drink_places_trung(trung_file):
    """retreive the drink place from the json file from trung
    Args:
        trung_file: json file from Trung
    Return: dict of (user -> UserPlaceTimeOnly)
    """
    PLACES = dict()
    PLACES[1] = "Bar"
    PLACES[2] = "Club"
    PLACES[3] = "Restaurant"
    PLACES[4] = "Private"
    PLACES[5] = "School/Uni"
    PLACES[6] = "Street/Urban"
    PLACES[7] = "Indoor Recreational"
    PLACES[8] = "Events"
    PLACES[9] = "Culture"
    PLACES[10] = "Traveling"
    PLACES[11] = "Other"
    PLACES[12] = "Unknown"
    PLACES[13] = "Outdoor/Park"
    drink_places = defaultdict(list)
    with open(trung_file, "r") as f:
        lines = f.read().split("\n")
        for line in lines:
            try:
                place = json.loads(line)
                pts_t = datetime.strptime(place["video_timestamp"], "%Y-%m-%d %H:%M:%S")
                place_str = PLACES[place["ptype_rec"]]
                user = place["user"]
                user_place_time_only = UserPlaceTimeOnly(pts_t, place_str, user)
                drink_places[user].append(user_place_time_only)
            except:
                pass
    return drink_places


def get_ambiance_places(ambiance_file):
    """retreive the drink place from the surveys ambiance file
    Args:
        ambiance_file: ambiance csv file
    Return: dict of (user -> UserPlaceTimeOnly)
    """
    df_ambiance = pd.read_csv(ambiance_file, sep=",", encoding="ISO-8859-1")
    user_places = defaultdict(list)
    for index, row in df_ambiance.iterrows():
        user = row["user"]
        pts_t = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
        if row["place_type"] == "personal":
            place = row["place_id_name"]
        else:
            place = row["place_type"]
        user_place_time_only = UserPlaceTimeOnly(pts_t, place, user)
        user_places[user].append(user_place_time_only)
    return user_places


def _convert_to_places_if_needed(user, stay_points, ambiance_places, trung_places):
    """convert the places UserPlaceTimeOnly into UserPlace"""
    if user in ambiance_places:
        ambiance_places[user] = [
            p.to_user_place_from_stay_points(
                stay_points, max_delta_time_ms=1000 * 60 * 3
            )
            for p in ambiance_places[user]
        ]
    if user in trung_places:
        trung_places[user] = [
            p.to_user_place_from_stay_points(
                stay_points, max_delta_time_ms=1000 * 60 * 3
            )
            for p in trung_places[user]
        ]


def _labelize(user, stay_regions, ambiance_places, trung_places):
    """Labelize the region with both ambiance places and trung places"""
    for stay_region in stay_regions:
        if user in ambiance_places:
            label = get_label_if_exist(stay_region, ambiance_places[user])
            if label is not None:
                stay_region.set_label(label)
        if user in trung_places:
            trung_label = get_label_if_exist(stay_region, trung_places[user])
            if trung_label is not None:
                stay_region.set_trung_label(trung_label)


def _create_locations(df):
    """create locations list from the list of locations."""
    locations = []
    for index, row in df.iterrows():
        accuracy = row["accuracy"]
        # if accuracy > 37:
        #     continue
        pts_t = datetime.fromtimestamp(row["timestamp"])
        location = YNLocationPoint(
            pts_t,
            row["latitude"],
            row["longitude"],
            accuracy,
            row["timezone"],
            row["night"],
        )
        locations.append(location)
    return locations


def write_to_json(json_output_file, gps_folder, ambiance_file=None, trung_file=None):
    """convert the data to a json file with StayPoints, StayRegion and LocationPoint.
    Args:
        json_output_file: file that will contain the data transformed
        gps_folder: folder that contain the gps records
        ambiance_file: file that contain ambiance file (from survey)
        trung_file: json file given by Trung that contain custom labels
    """
    location_files = glob(join(gps_folder, "*_location.csv"))
    ambiance_places = (
        dict() if ambiance_file is None else get_ambiance_places(ambiance_file)
    )
    trung_places = dict() if trung_file is None else get_drink_places_trung(trung_file)
    list_of_users = []
    bar = Bar("processing", max=len(location_files))
    with open(json_output_file, "w") as f:
        for location_file in location_files:
            bar.next()
            df = pd.read_csv(location_file)
            try:
                user = df["userid"].tolist()[0]
            except IndexError:
                continue
            locations = _create_locations(df)

            stay_points = yn_estimate_stay_points(locations)
            if len(stay_points) > 1:
                stay_regions = yn_estimate_stay_regions(
                    stay_points, accuracy_aware=False
                )
                _convert_to_places_if_needed(
                    user, stay_points, ambiance_places, trung_places
                )
                _labelize(user, stay_regions, ambiance_places, trung_places)
                yn_user = YNUser(
                    user_id=user, stay_points=stay_points, stay_regions=stay_regions
                )
                list_of_users.append(yn_user.to_dict())
        f.write(json.dumps(list_of_users, indent=4))
    bar.finish()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="convert the data to a json file with StayPoints, StayRegion and LocationPoint."
    )
    parser.add_argument(
        "json_output_file", type=str, help="file that will contain the data transformed"
    )
    parser.add_argument(
        "gps_folder", type=str, help="folder that contain the gps records"
    )
    parser.add_argument(
        "--ambiance_file",
        type=str,
        help="file that contain ambiance file (from survey)",
    )
    parser.add_argument(
        "--trung_file",
        type=str,
        help="json file given by Trung that contain custom labels",
    )
    args = parser.parse_args()
    write_to_json(
        args.json_output_file, args.gps_folder, args.ambiance_file, args.trung_file
    )
