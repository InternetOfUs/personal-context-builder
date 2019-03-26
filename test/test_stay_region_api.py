import unittest
import json
import datetime
from sanic_app import app
import config
from random import randint
from wenet_models import LocationPoint
from wenet_algo import estimate_stay_points


class StayPointAPITestCase(unittest.TestCase):
    def test_simple_2_region(self):
        day_one = datetime.datetime(2019, 2, 6, 11, 16)
        locations = []
        n = 100
        for i in range(n):
            if i < n // 2:
                pt = LocationPoint(day_one, randint(-1, 0), randint(-1, 0))
            else:
                pt = LocationPoint(day_one, randint(50, 51), randint(150, 151))
            locations.append(pt)
            day_one = day_one + datetime.timedelta(seconds=5)

        stay_points = estimate_stay_points(
            locations, time_min_ms=4999, distance_max_m=10 ** 5
        )
        stay_points = [p.__dict__ for p in stay_points]
        for staypoint in stay_points:
            staypoint["_t_start"] = staypoint["_t_start"].strftime(
                config.DEFAULT_DATETIME_FORMAT
            )
            staypoint["_t_stop"] = staypoint["_t_stop"].strftime(
                config.DEFAULT_DATETIME_FORMAT
            )
        stay_points_dict = {}
        stay_points_dict["staypoints"] = stay_points
        stay_points_dict["distance_threshold_m"] = 10 ** 7
        _, response = app.test_client.post(
            "/stayregionsoneday/", data=json.dumps(stay_points_dict)
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(len(response.json.get("stayregions")), 2)

    def test_simple_2x1_region(self):
        day_one = datetime.datetime(2019, 2, 6, 11, 16)
        day_two = datetime.datetime(2019, 2, 7, 11, 16)
        locations = []
        n = 100
        for i in range(n):
            if i < n // 2:
                pt = LocationPoint(day_one, randint(-1, 0), randint(-1, 0))
                day_one = day_one + datetime.timedelta(seconds=5)
            else:
                pt = LocationPoint(day_two, randint(50, 51), randint(150, 151))
                day_two = day_two + datetime.timedelta(seconds=5)
            locations.append(pt)

        stay_points = estimate_stay_points(
            locations, time_min_ms=4999, distance_max_m=10 ** 5
        )
        stay_points = [p.__dict__ for p in stay_points]
        for staypoint in stay_points:
            staypoint["_t_start"] = staypoint["_t_start"].strftime(
                config.DEFAULT_DATETIME_FORMAT
            )
            staypoint["_t_stop"] = staypoint["_t_stop"].strftime(
                config.DEFAULT_DATETIME_FORMAT
            )
        stay_points_dict = {}
        stay_points_dict["staypoints"] = stay_points
        stay_points_dict["distance_threshold_m"] = 10 ** 7
        _, response = app.test_client.post(
            "/stayregions/", data=json.dumps(stay_points_dict)
        )
        self.assertEqual(response.status, 200)
        res = response.json
        self.assertEqual(len(res), 2)
