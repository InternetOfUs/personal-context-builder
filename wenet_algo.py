"""
module that contain algorithms used for the wenet project
"""

from typing import List, Set
import math
from operator import add
from functools import reduce
from math import sin, cos, sqrt, atan2, radians
from wenet_models import StayPoint, LocationPoint


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
    time_min_ms: int = 5 * 60 * 1000,
    time_max_ms: int = 4 * 60 * 60 * 1000,
    distance_max_m: int = 200,
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
                    t_stop = locations[j - 1]._pts_t
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
