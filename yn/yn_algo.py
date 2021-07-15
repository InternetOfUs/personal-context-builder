""" Y@N algorithms
"""
from collections import defaultdict
from typing import Dict, List, Set

import numpy as np
from sklearn.cluster import DBSCAN

from personal_context_builder import config
from personal_context_builder.wenet_algo import estimate_centroid
from personal_context_builder.wenet_tools import space_distance_m_by_vect
from yn.yn_models import YNLocationPoint, YNStayPoint, YNStayRegion


def create_stay_point(locations):
    centroid = estimate_centroid(locations)
    maximum_accuracy = max([l._accuracy_m for l in locations])
    t_start = locations[0]._pts_t
    t_stop = locations[-1]._pts_t
    stay_point = YNStayPoint(
        t_start,
        t_stop,
        centroid._lat,
        centroid._lng,
        accuracy_m=maximum_accuracy,
        timezone=locations[0]._timezone,
        night_id=locations[0]._night_id,
    )
    return stay_point


def yn_estimate_stay_points(
    locations: List[YNLocationPoint],
    time_min_ms: int = config.PCB_STAYPOINTS_TIME_MIN_MS,
    time_max_ms: int = config.PCB_STAYPOINTS_TIME_MAX_MS,
    distance_max_m: int = config.PCB_STAYPOINTS_DISTANCE_MAX_M,
) -> Set[YNStayPoint]:
    """
    Estimate stay points from a list of location points

    version from scratch

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
    len_locations = len(locations)
    if not len_locations > 1:
        return stay_points
    i = 1
    previous_location = locations[0]
    sublist = [previous_location]
    while i < len_locations:
        current_location = locations[i]
        dt = previous_location.time_difference_ms(current_location)
        dt_start_end = sublist[0].time_difference_ms(current_location)
        distance = previous_location.space_distance_m(current_location)
        if (
            dt > time_min_ms
            and dt_start_end < time_max_ms
            and distance < distance_max_m
        ):
            sublist.append(current_location)
        else:
            if len(sublist) > 1:
                stay_point = create_stay_point(sublist)
                stay_points.add(stay_point)
            sublist = [current_location]
        previous_location = current_location
        i = i + 1
    if len(sublist) > 1:
        stay_point = create_stay_point(sublist)
        stay_points.add(stay_point)
    return stay_points


def yn_estimate_stay_regions(
    staypoints: List[YNStayPoint],
    distance_threshold_m: int = config.PCB_STAYREGION_DISTANCE_THRESHOLD_M,
    accuracy_aware: bool = True,
) -> Set[YNStayRegion]:
    """
    Estimate stay regions from a list of stay points

    TODO cite paper here
    TODO use grid-based clustering as in the paper
    TODO Test outliers (-1)
    Args:
        staypoints: list of staypoint to use to extract stay region
        distance_threshold_m: distance of the threshold in meter
        accuracy_aware: if true, take accuracy into consideration when building regions
    """
    clustered_staypoints = defaultdict(list)
    staypoint_matrix = np.array([[p._lat, p._lng] for p in staypoints])
    clustering = DBSCAN(
        eps=distance_threshold_m, metric=space_distance_m_by_vect, min_samples=2
    ).fit(staypoint_matrix)
    labels = clustering.labels_
    for label, staypoint in zip(labels, staypoints):
        if label == -1:
            continue
        clustered_staypoints[label].append(staypoint)
    results = []
    for _, staypoints in clustered_staypoints.items():
        if accuracy_aware:
            region = YNStayRegion.create_from_cluster_maximum_surround(staypoints)
        else:
            region = YNStayRegion.create_from_cluster(staypoints)
        results.append(region)
    return results
