"""
module for Y@N specific models

Use wenet models as bases
"""

import hashlib
import json
from copy import deepcopy

import numpy as np

import personal_context_builder.wenet_models as wm
from personal_context_builder import config


class YNUser(object):
    """Y@N user information"""

    def __init__(self, user_id="", stay_points=None, stay_regions=None):
        self._user_id = user_id
        self._stay_points = {} if stay_points is None else stay_points
        self._stay_regions = {} if stay_regions is None else stay_regions

    def to_dict(self):
        my_dict = dict()
        my_dict["user_id"] = self._user_id
        my_dict["stay_points_list"] = [s.to_dict() for s in self._stay_points]
        my_dict["stay_regions_list"] = [r.to_dict() for r in self._stay_regions]
        return my_dict

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)


class YNLocationPoint(wm.LocationPoint):
    """Y@N Location Point"""

    def __init__(self, pts_t, lat, lng, accuracy_m=0, timezone="", night_id=None):
        super().__init__(pts_t, lat, lng, accuracy_m)
        self._timezone = timezone
        self._night_id = night_id


class YNStayPoint(wm.StayPoint):
    """Y@N Stay Point"""

    def __init__(
        self, t_start, t_stop, lat, lng, accuracy_m=0, timezone="CET", night_id=None
    ):
        super().__init__(t_start, t_stop, lat, lng, accuracy_m)
        self._timezone = timezone
        self._night_id = night_id
        self._id = hashlib.sha256(self._str_without_id().encode("utf-8")).hexdigest()

    def _str_without_id(self):
        return f"timezone: {self._timezone} " + super().__str__()

    def __str__(self):
        return f"ID: {self._id} " + self._str_without_id()

    def __hash__(self):
        return self._str_without_id().__hash__()

    def to_dict(self):
        return {
            "lat": self._lat,
            "lng": self._lng,
            "acc": self._accuracy_m,
            "night_id": self._night_id,
            "start_datetime": self._t_start.strftime(config.DEFAULT_DATETIME_FORMAT),
            "end_datetime": self._t_stop.strftime(config.DEFAULT_DATETIME_FORMAT),
            "timezone": self._timezone,
            "stay_point_id": self._id,
        }


class YNStayRegion(wm.StayRegion):
    """Y@N Stay Region"""

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
        stay_points=None,
    ):
        super().__init__(
            t_start,
            t_stop,
            centroid_lat,
            centroid_lng,
            topleft_lat,
            topleft_lng,
            bottomright_lat,
            bottomright_lng,
        )
        if stay_points is not None:
            self.set_stay_points(stay_points)
        self._id = hashlib.sha256(super().__str__().encode("utf-8")).hexdigest()
        self._label = None
        self._trung_label = None

    def set_stay_points(self, stay_points):
        self._stay_points = deepcopy(stay_points)

    def set_label(self, label):
        self._label = label

    def set_trung_label(self, label):
        self._trung_label = label

    def to_dict(self):
        my_dict = dict()

        my_dict["start_datetime"] = self._t_start.strftime(
            config.DEFAULT_DATETIME_FORMAT
        )
        my_dict["end_datetime"] = self._t_stop.strftime(config.DEFAULT_DATETIME_FORMAT)
        if self._stay_points is not None and len(self._stay_points) > 0:
            my_dict["stay_points"] = [s._id for s in self._stay_points]
            my_dict["timezone"] = self._stay_points[0]._timezone
        if self._label is not None:
            my_dict["label"] = self._label
        if self._trung_label is not None:
            my_dict["trung_label"] = self._trung_label

        return my_dict

    @classmethod
    def create_from_cluster(cls, staypoints):
        region = super().create_from_cluster(staypoints)
        region.set_stay_points(staypoints)
        return region
