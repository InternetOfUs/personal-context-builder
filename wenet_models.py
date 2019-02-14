"""
module with models and data structure relevant to wenet project
"""
import math
from math import sin, cos, sqrt, atan2, radians
from wenet_tools import space_distance_m, time_difference_ms
import numpy as np


class GPSPoint(object):
    """
    base class or all points-related models
    """

    def __init__(self, lat, lng):
        self._lat = lat
        self._lng = lng

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
        return GPSPoint(lat, lng)

    def __sub__(self, other):
        lat = self._lat - other._lat
        lng = self._lng - other._lng
        return GPSPoint(lat, lng)

    def __truediv__(self, other):
        if isinstance(other, GPSPoint):
            lat = self._lat / other._lat
            lng = self._lng / other._lng
        else:
            lat = self._lat / other
            lng = self._lng / other
        return GPSPoint(lat, lng)

    def __mul__(self, other):
        if isinstance(other, GPSPoint):
            lat = self._lat * other._lat
            lng = self._lng * other._lng
        else:
            lat = self._lat * other
            lng = self._lng * other
        return GPSPoint(lat, lng)

    def __hash__(self):
        return str(self).__hash__()

    def __str__(self):
        return f"{self._lat:.5f}, {self._lng:.5f}"

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class LocationPoint(GPSPoint):
    """
    class that handle timestamped gps points
    """

    def __init__(self, pts_t, lat, lng):
        super().__init__(lat, lng)
        self._pts_t = pts_t

    def time_difference_ms(self, other):
        """ Compute the time difference in (ms)

        Args:
            other: other LocationPoint instance to compare

        Return: time difference in ms
        """
        return time_difference_ms(self._pts_t, other._pts_t)

    def __add__(self, other):
        point = super().__add__(other)
        return LocationPoint(self._pts_t, point._lat, point._lng)

    def __sub__(self, other):
        point = super().__sub__(other)
        return LocationPoint(self._pts_t, point._lat, point._lng)

    def __truediv__(self, other):
        point = super().__truediv__(other)
        return LocationPoint(self._pts_t, point._lat, point._lng)

    def __mul__(self, other):
        point = super().__mul__(other)
        return LocationPoint(self._pts_t, point._lat, point._lng)

    def __str__(self):
        return super().__str__() + f" [{self._pts_t}]"


class StayPoint(GPSPoint):
    """
    class for stay point
    """

    def __init__(self, t_start, t_stop, lat, lng):
        super().__init__(lat, lng)
        self._t_start = t_start
        self._t_stop = t_stop

    def __str__(self):
        return super().__str__() + f"[{self._t_start} to {self._t_stop}]"


class StayRegion(StayPoint):
    def __init__(
        self,
        t_start,
        t_stop,
        centroid_lat,
        centroid_lng,
        topleft_lat,
        topleft_lng,
        bottomright_lat,
        bottomright_lng,
    ):
        """ Constructor

        Args:
            t_start: time when enter the region the first time
            t_stop: time when go out of the region the last time
            centroid_lat: latitude of the centroid of the staypoints
            centroid_lng: longitude of the centroid of the staypoints
            topleft_lat: highest latitude in the staypoints
            topleft_lng: highest longitude in the staypoints
            bottomright_lat: smallest latitude in the staypoints
            bottomrght_lng: smallest longitude in the staypoints
        """
        super().__init__(t_start, t_stop, centroid_lat, centroid_lng)
        self._topleft_lat = topleft_lat
        self._topleft_lng = topleft_lng
        self._bottomright_lat = bottomright_lat
        self._bottomright_lng = bottomright_lng

    def __contains__(self, key: GPSPoint):
        lat = key._lat
        lng = key._lng
        return not (
            lat < self._bottomright_lat
            or lat > self._topleft_lat
            or lng < self._bottomright_lat
            or lng > self._topleft_lng
        )

    @classmethod
    def create_from_cluster(cls, staypoints):
        """ Create a region from a list of staypoints

        Args:
            staypoints: list of staypoints

        Return: a StayRegion instance
        """
        min_t_start = min(staypoints, key=lambda p: p._t_start)._t_start
        max_t_stop = max(staypoints, key=lambda p: p._t_stop)._t_stop
        lat_mean = np.average([s._lat for s in staypoints])
        lng_mean = np.average([s._lng for s in staypoints])
        topleft_lat = max(staypoints, key=lambda p: p._lat)._lat
        topleft_lng = max(staypoints, key=lambda p: p._lng)._lng
        bottomright_lat = min(staypoints, key=lambda p: p._lat)._lat
        bottomright_lng = min(staypoints, key=lambda p: p._lng)._lng
        region = StayRegion(
            min_t_start,
            max_t_stop,
            lat_mean,
            lng_mean,
            topleft_lat,
            topleft_lng,
            bottomright_lat,
            bottomright_lng,
        )
        return region


class LabelledStayRegion(StayRegion):
    """ StayRegion with label
    """

    def __init__(self, label, stay_region: StayRegion):
        """ Constructor

        Args:
            label: label for the StayRegion
            stay_region: StayRegion instance that will be copied
        """
        super().__init__(
            stay_region._t_start,
            stay_region._t_stop,
            stay_region._lat,
            stay_region._lng,
            stay_region._topleft_lat,
            stay_region._topleft_lng,
            stay_region._bottomright_lat,
            stay_region._bottomright_lng,
        )
        self._label = label
