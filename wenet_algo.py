"""
module that contain algorithms used for the wenet project
"""

from typing import List, Set, Dict
import math
from operator import add
from functools import reduce
from wenet_models import StayPoint, LocationPoint, StayRegion
import config
from collections import defaultdict
from sklearn.cluster import DBSCAN
import numpy as np
from wenet_tools import space_distance_m_by_vect


def estimate_centroid(locations: List[LocationPoint]) -> LocationPoint:
    """
    compute the average for all locations combined

    Args:
        locations: the list of location points

    Return:
        a location point located as the average of all points
    """
    return reduce(add, locations) / len(locations)


def estimate_stay_points(
    locations: List[LocationPoint],
    time_min_ms: int = config.DEFAULT_STAYPOINTS_TIME_MIN_MS,
    time_max_ms: int = config.DEFAULT_STAYPOINTS_TIME_MAX_MS,
    distance_max_m: int = config.DEFAULT_STAYPOINTS_DISTANCE_MAX_M,
) -> Set[StayPoint]:
    """
    Estimate stay points from a list of location points

    TODO cite paper here
    Args:
        locations: the list of location points to process
        time_min_ms: minimum delta time (ms) allowed to create a StayPoint
        time_max_ms: maximum delta time (ms) allowed to create a StayPoint
        distance_max_m maximum distance (m) allowed to create a StayPoint

    Return:
        Set of StayPoint

    """
    locations = sorted(locations, key=lambda l: l._pts_t)
    stay_points = set()
    i = 0
    len_locations = len(locations)
    while i < len_locations:
        j = i + 1
        while j < len_locations:
            dt = locations[j].time_difference_ms(locations[j - 1])
            if dt > time_max_ms:
                i = j
                break
            distance = locations[i].space_distance_m(locations[j])
            if distance < distance_max_m:
                if dt > time_min_ms:
                    centroid = estimate_centroid(locations[i : j + 1])
                    t_start = locations[i]._pts_t
                    t_stop = locations[j]._pts_t
                    stay_point = StayPoint(
                        t_start, t_stop, centroid._lat, centroid._lng
                    )
                    stay_points.add(stay_point)
                i = j
                break
            j = j + 1
        # if not, can be stuck
        i += 1
    return stay_points


def estimate_stay_regions_per_day(
    staypoints: List[StayPoint],
    distance_threshold_m: int = config.DEFAULT_STAYREGION_DISTANCE_THRESHOLD_M,
) -> Dict[str, List[StayRegion]]:
    """
    Estimate stay regions from a list of stay points

    Args:
        staypoints: list of staypoint to use to extract stay region
        distance_threshold_m: distance of the threshold in meter

    Return:
        dict with key is a day and values are list of StayRegion.
        day format is YYYY-MM-DD
    """
    stay_points_per_day = defaultdict(list)
    stay_regions_per_day = dict()
    for staypoint in staypoints:
        stay_points_per_day[staypoint._t_start.strftime("%Y-%m-%d")].append(staypoint)

    for day, values in stay_points_per_day.items():
        stay_regions_per_day[day] = estimate_stay_regions(values, distance_threshold_m)
    return stay_regions_per_day


def estimate_stay_regions(
    staypoints: List[StayPoint],
    distance_threshold_m: int = config.DEFAULT_STAYREGION_DISTANCE_THRESHOLD_M,
) -> Set[StayRegion]:
    """
    Estimate stay regions from a list of stay points

    TODO cite paper here
    TODO use custom metric to match lat/lng
    TODO use grid-based clustering as in the paper
    TODO Test outliers (-1)
    Args:
        staypoints: list of staypoint to use to extract stay region
        distance_threshold_m: distance of the threshold in meter
    """
    clustered_staypoints = defaultdict(list)
    staypoint_matrix = np.array([[p._lat, p._lng] for p in staypoints])
    clustering = DBSCAN(eps=distance_threshold_m, metric=space_distance_m_by_vect).fit(
        staypoint_matrix
    )
    labels = clustering.labels_
    for label, staypoint in zip(labels, staypoints):
        if label == -1:
            continue
        clustered_staypoints[label].append(staypoint)
    results = []
    for _, staypoints in clustered_staypoints.items():
        # TODO average or median should be better
        # TODO optimize for less traversal of staypoints
        min_t_start = min(staypoints, key=lambda p: p._t_start)._t_start
        max_t_stop = max(staypoints, key=lambda p: p._t_stop)._t_stop
        lat_mean = np.average([s._lat for s in staypoints])
        lng_mean = np.average([s._lng for s in staypoints])
        region = StayRegion(min_t_start, max_t_stop, lat_mean, lng_mean)
        results.append(region)
    return results
