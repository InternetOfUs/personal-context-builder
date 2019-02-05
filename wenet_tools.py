"""
module with general-purpose helper/tools function
"""
from math import sin, cos, sqrt, atan2, radians


def time_difference_ms(time_1, time_2):
    """ Compute the time difference in (ms)

    Args:
        time1: first operand time
        time2: second operand time

    Return: time difference in ms
    """
    return (time_1 - time_2).total_seconds() * 1000


def space_distance_m(lat1, lng1, lat2, lng2):
    """ Compute the spatial distance in meters

    Args:
        lat1: first point latitude
        lng1: first point longitude
        lat2: second point latitude
        lng2: second point longitude

    Return: distance in meters
    """
    R = 6_373_000.0

    lat1 = radians(lat1)
    lng1 = radians(lng1)
    lat2 = radians(lat2)
    lng2 = radians(lng2)

    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = (sin(dlat / 2)) ** 2 + cos(lat1) * cos(lat2) * (sin(dlon / 2)) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance
