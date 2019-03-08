""" Y@N algorithms
"""
import config
from typing import List, Set, Dict
from yn.yn_models import YNStayPoint, YNLocationPoint, YNStayRegion
from wenet_algo import estimate_centroid
from collections import defaultdict
from sklearn.cluster import DBSCAN
import numpy as np
from wenet_tools import space_distance_m_by_vect


def yn_estimate_stay_points(
    locations: List[YNLocationPoint],
    time_min_ms: int = config.DEFAULT_STAYPOINTS_TIME_MIN_MS,
    time_max_ms: int = config.DEFAULT_STAYPOINTS_TIME_MAX_MS,
    distance_max_m: int = config.DEFAULT_STAYPOINTS_DISTANCE_MAX_M,
) -> Set[YNStayPoint]:
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
                    maximum_accuracy = max(
                        [l._accuracy_m for l in locations[i : j + 1]]
                    )
                    t_start = locations[i]._pts_t
                    t_stop = locations[j]._pts_t
                    stay_point = YNStayPoint(
                        t_start,
                        t_stop,
                        centroid._lat,
                        centroid._lng,
                        accuracy_m=maximum_accuracy,
                        timezone=locations[i]._timezone,
                        night_id=locations[i]._night_id,
                    )
                    stay_points.add(stay_point)
                i = j
                break
            j = j + 1
        # if not, can be stuck
        i += 1
    return stay_points


def yn_estimate_stay_regions(
    staypoints: List[YNStayPoint],
    distance_threshold_m: int = config.DEFAULT_STAYREGION_DISTANCE_THRESHOLD_M,
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
