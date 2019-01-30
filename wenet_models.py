"""
module with models and data structure relevant to wenet project
"""
import math
from math import sin, cos, sqrt, atan2, radians


class LocationPoint(object):
    """
    class that handle timestamped gps points
    """

    def __init__(self, pts_t, lat, lng):
        self._pts_t = pts_t
        self._lat = lat
        self._lng = lng

    def time_difference_ms(self, other):
        return (self._pts_t - other._pts_t).total_seconds() * 1000

    def space_distance(self, other):
        R = 6_373_000.0
        lat1, lng1 = self._lat, self._lng
        lat2, lng2 = other._lat, self._lng

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

    def __add__(self, other):
        pts_t = self._pts_t + other._pts_t
        lat = self._lat + other._lat
        lng = self._lng + other._lng
        return LocationPoint(pts_t, lat, lng)

    def __sub__(self, other):
        pts_t = self._pts_t - other._pts_t
        lat = self._lat - other._lat
        lng = self._lng - other._lng
        return LocationPoint(pts_t, lat, lng)

    def __truediv__(self, other):
        if isinstance(other, LocationPoint):
            pts_t = self._pts_t / other._pts_t
            lat = self._lat / other._lat
            lng = self._lng / other._lng
        else:
            pts_t = self._pts_t / other
            lat = self._lat / other
            lng = self._lng / other
        return LocationPoint(pts_t, lat, lng)

    def __mul__(self, other):
        if isinstance(other, LocationPoint):
            pts_t = self._pts_t * other._pts_t
            lat = self._lat * other._lat
            lng = self._lng * other._lng
        else:
            pts_t = self._pts_t * other
            lat = self._lat * other
            lng = self._lng * other
        return LocationPoint(pts_t, lat, lng)

    def __hash__(self):
        return str(self).__hash__()

    def __str__(self):
        return f"{self._lat:.5f}, {self._lng:.5f} [{self._pts_t}]"

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class StayPoint(object):
    """
    class for stay point
    """

    def __init__(self, t_start, t_stop, lat, lng):
        self._t_start = t_start
        self._t_stop = t_stop
        self._lat = lat
        self._lng = lng

    def __hash__(self):
        return str(self).__hash__()

    def __str__(self):
        return f"{self._lat:.5f}, {self._lng:.5f} [{self._t_start} to {self._t_stop}]"

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()
