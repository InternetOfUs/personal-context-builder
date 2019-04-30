"""
module with models and data structure relevant to wenet project
"""
import math
import datetime
from math import sin, cos, sqrt, atan2, radians
from wenet_tools import space_distance_m, time_difference_ms
import config
import numpy as np
from typing import List
from functools import partial
from random import random


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
        lat2, lng2 = other._lat, other._lng
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

    def __init__(self, pts_t, lat, lng, accuracy_m=0):
        super().__init__(lat, lng)
        self._pts_t = pts_t
        self._accuracy_m = accuracy_m

    def time_difference_ms(self, other):
        """ Compute the time difference in (ms)

        Args:
            other: other LocationPoint instance to compare

        Return: time difference in ms
        """
        return time_difference_ms(self._pts_t, other._pts_t)

    def __add__(self, other):
        point = super().__add__(other)
        return LocationPoint(self._pts_t, point._lat, point._lng, self._accuracy_m)

    def __sub__(self, other):
        point = super().__sub__(other)
        return LocationPoint(self._pts_t, point._lat, point._lng, self._accuracy_m)

    def __truediv__(self, other):
        point = super().__truediv__(other)
        return LocationPoint(self._pts_t, point._lat, point._lng, self._accuracy_m)

    def __mul__(self, other):
        point = super().__mul__(other)
        return LocationPoint(self._pts_t, point._lat, point._lng, self._accuracy_m)

    def __str__(self):
        return super().__str__() + f" [{self._pts_t}]"


class UserLocationPoint(LocationPoint):
    """
    class that handle timestamped gps points
    """

    def __init__(self, pts_t, lat, lng, accuracy_m=0, user="anonymous"):
        super().__init__(pts_t, lat, lng, accuracy_m)
        self._user = user

    def __str__(self):
        return f"[{self._user}] " + super().__str__()

    def __add__(self, other):
        point = super().__add__(other)
        return UserLocationPoint(
            self._pts_t, point._lat, point._lng, self._accuracy_m, self._user
        )

    def __sub__(self, other):
        point = super().__sub__(other)
        return UserLocationPoint(
            self._pts_t, point._lat, point._lng, self._accuracy_m, self._user
        )

    def __truediv__(self, other):
        point = super().__truediv__(other)
        return UserLocationPoint(
            self._pts_t, point._lat, point._lng, self._accuracy_m, self._user
        )

    def __mul__(self, other):
        point = super().__mul__(other)
        return UserLocationPoint(
            self._pts_t, point._lat, point._lng, self._accuracy_m, self._user
        )


class StayPoint(GPSPoint):
    """
    class for stay point
    """

    def __init__(self, t_start, t_stop, lat, lng, accuracy_m=0):
        super().__init__(lat, lng)
        self._t_start = t_start
        self._t_stop = t_stop
        self._accuracy_m = accuracy_m

    def __str__(self):
        return (
            super().__str__()
            + f"[{self._t_start} to {self._t_stop}] +- {self._accuracy_m} m"
        )

    def _get_min_max_latitude_from_accuracy(self, delta_inc):
        cpt = 0
        distance = space_distance_m(
            self._lat, self._lng, self._lat + cpt * delta_inc, self._lng
        )
        while distance <= self._accuracy_m:
            distance = space_distance_m(
                self._lat, self._lng, self._lat + cpt * delta_inc, self._lng
            )
            cpt += 1
        min_lat = self._lat - delta_inc * cpt
        max_lat = self._lat + delta_inc * cpt
        return min_lat, max_lat

    def _get_min_max_longitude_from_accuracy(self, delta_inc):
        cpt = 0
        distance = space_distance_m(
            self._lat, self._lng, self._lat + cpt * delta_inc, self._lng
        )
        while distance <= self._accuracy_m:
            distance = space_distance_m(
                self._lat, self._lng, self._lat, self._lng + cpt * delta_inc
            )
            cpt += 1
        min_lng = self._lng - delta_inc * cpt
        max_lng = self._lng + delta_inc * cpt
        return min_lng, max_lng

    def _get_surrouder_points(self, delta_inc, nb_wanted_points=100):
        """ generate 100 points that are around this points.

        Inspired of monte-carlo method:
            - get a square of 2x accuracy, centered in lat/lng
            - generate a random points inside
            - keep points that is close to the accuracy circle border
            - repeat until 100 points

        Args:
        delta_inc: increment step at each iteration, both lat and lng

        Return: 100 staypoints as list, or 1 staypoint if accuracy is 0
        """
        if self._accuracy_m == 0:
            return [self]
        min_lat, max_lat = self._get_min_max_latitude_from_accuracy(delta_inc)
        min_lng, max_lng = self._get_min_max_longitude_from_accuracy(delta_inc)
        nb_points = 0
        points = []
        while nb_points < nb_wanted_points:
            random_lat = random() * (max_lat - min_lat) + min_lat
            random_lng = random() * (max_lng - min_lng) + min_lng
            distance = space_distance_m(self._lat, self._lng, random_lat, random_lng)
            if abs(distance - self._accuracy_m) < 1:
                points.append(
                    StayPoint(self._t_start, self._t_stop, random_lat, random_lng, 0)
                )
                nb_points += 1
        return points


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

    def __str__(self):
        my_str = f"\n\t{self._topleft_lat} : {self._topleft_lng}\n"
        my_str += f"\t\t{self._bottomright_lat} : {self._bottomright_lng}"
        return super().__str__() + my_str

    def __contains__(self, key: GPSPoint):
        lat = key._lat
        lng = key._lng
        return not (
            lat < self._bottomright_lat
            or lat > self._topleft_lat
            or lng < self._bottomright_lng
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
        region = cls(
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

    @classmethod
    def create_from_cluster_maximum_surround(
        cls, staypoints, delta_inc=config.DEFAULT_STAYREGION_INC_DELTA
    ):
        """ Create a region from a list of staypoints
        surround the points based on accuracy of them

        Args:
            staypoints: list of staypoints

        Return: a StayRegion instance
        """
        englobing_stay_points = []
        for stay_point in staypoints:
            englobing_stay_points += stay_point._get_surrouder_points(delta_inc)
        return cls.create_from_cluster(englobing_stay_points)


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


class UserPlace(LocationPoint):
    """ Class that store user defined place
    """

    def __init__(self, pts_t, lat, lng, label, user="anonymous"):
        super().__init__(pts_t, lat, lng)
        self._label = label
        self._user = user


class UserPlaceTimeOnly(object):
    """ Class that store user defined place
    """

    def __init__(self, pts_t, label, user="anonymous"):
        self._pts_t = pts_t
        self._label = label
        self._user = user

    def to_user_place(
        self,
        locations: List[LocationPoint],
        max_delta_time_ms=config.DEFAULT_USERPLACE_TIME_MAX_DELTA_MS,
    ):
        compare_dt = partial(time_difference_ms, self._pts_t)
        closest_location = min(locations, key=lambda x: compare_dt(x._pts_t))
        if compare_dt(closest_location._pts_t) > max_delta_time_ms:
            return None
        else:
            return UserPlace(
                self._pts_t,
                closest_location._lat,
                closest_location._lng,
                self._label,
                self._user,
            )

    def to_user_place_from_stay_points(
        self,
        stay_points: List[StayPoint],
        max_delta_time_ms=config.DEFAULT_USERPLACE_TIME_MAX_DELTA_MS,
        stay_points_sample_ms=config.DEFAULT_USERPLACE_STAY_POINT_SAMPLING,
    ):
        locations = []
        t_increment = datetime.timedelta(milliseconds=stay_points_sample_ms)
        for stay_point in stay_points:
            dt = stay_point._t_start
            while dt < stay_point._t_stop:
                dt += t_increment
                location = LocationPoint(dt, stay_point._lat, stay_point._lng)
                locations.append(location)
        return self.to_user_place(locations, max_delta_time_ms=max_delta_time_ms)
