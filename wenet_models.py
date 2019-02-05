"""
module with models and data structure relevant to wenet project
"""
import math
from math import sin, cos, sqrt, atan2, radians
from wenet_tools import space_distance_m, time_difference_ms


class LocationPoint(object):
    """
    class that handle timestamped gps points
    """

    def __init__(self, pts_t, lat, lng):
        self._pts_t = pts_t
        self._lat = lat
        self._lng = lng

    def time_difference_ms(self, other):
        """ Compute the time difference in (ms)

        Args:
            other: other LocationPoint instance to compare

        Return: time difference in ms
        """
        return time_difference_ms(self._pts_t, other._pts_t)

    def space_distance_m(self, other):
        """ Compute the spatial distance in meters

        Args:
            other: other LocationPoint instance to compare

        Return: distance in meters
        """
        lat1, lng1 = self._lat, self._lng
        lat2, lng2 = other._lat, self._lng
        return space_distance_m(lat1, lng1, lat2, lng2)

    def __add__(self, other):
        lat = self._lat + other._lat
        lng = self._lng + other._lng
        return LocationPoint(self._pts_t, lat, lng)

    def __sub__(self, other):
        lat = self._lat - other._lat
        lng = self._lng - other._lng
        return LocationPoint(self._pts_t, lat, lng)

    def __truediv__(self, other):
        if isinstance(other, LocationPoint):
            lat = self._lat / other._lat
            lng = self._lng / other._lng
        else:
            lat = self._lat / other
            lng = self._lng / other
        return LocationPoint(self._pts_t, lat, lng)

    def __mul__(self, other):
        if isinstance(other, LocationPoint):
            lat = self._lat * other._lat
            lng = self._lng * other._lng
        else:
            lat = self._lat * other
            lng = self._lng * other
        return LocationPoint(self._pts_t, lat, lng)

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


class StayRegion(StayPoint):
    def __init__(self, t_start, t_stop, lat, lng):
        super().__init__(t_start, t_stop, lat, lng)
