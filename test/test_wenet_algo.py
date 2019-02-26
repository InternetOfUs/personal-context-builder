import unittest
import datetime
from copy import deepcopy
from random import randint

from wenet_models import LocationPoint, StayRegion, UserPlace
from wenet_algo import (
    estimate_centroid,
    estimate_stay_points,
    estimate_stay_regions,
    estimate_stay_regions_per_day,
    labelize_stay_region,
)


class WenetAlgoTestCase(unittest.TestCase):
    def test_estimate_centroid(self):
        t1 = datetime.datetime.now()
        pt1 = LocationPoint(t1, 0, 0)
        pt2 = LocationPoint(t1, 1, 1)
        pt3 = LocationPoint(t1, 2, 2)

        res = estimate_centroid([pt1, pt2, pt3])
        self.assertTrue(res._lat == 1 and res._lng == 1)

    def test_estimate_stay_points_find_a_point_time(self):
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(seconds=5)
        pt1 = LocationPoint(t1, 1, 1)
        pt2 = LocationPoint(t2, 1, 1)

        res = estimate_stay_points([pt1, pt2], time_min_ms=4999)
        self.assertTrue(len(res) == 1)

    def test_estimate_stay_points_dont_find_a_point_time(self):
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(seconds=5)
        pt1 = LocationPoint(t1, 1, 1)
        pt2 = LocationPoint(t2, 1, 1)

        res = estimate_stay_points([pt1, pt2], time_min_ms=5000)
        self.assertTrue(len(res) == 0)

    def test_estimate_stay_points_find_a_point_time_max(self):
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(seconds=5)
        pt1 = LocationPoint(t1, 1, 1)
        pt2 = LocationPoint(t2, 1, 1)

        res = estimate_stay_points([pt1, pt2], time_max_ms=5001, time_min_ms=4999)
        self.assertTrue(len(res) == 1)

    def test_estimate_stay_points_dont_find_a_point_time_max(self):
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(seconds=5)
        pt1 = LocationPoint(t1, 1, 1)
        pt2 = LocationPoint(t2, 1, 1)

        res = estimate_stay_points([pt1, pt2], time_max_ms=4999, time_min_ms=4999)
        self.assertTrue(len(res) == 0)

    def test_estimate_stay_points_dont_find_a_point_distance(self):
        martigny_lat = 46.101965
        martigny_lng = 7.079912
        neuchatel_lat = 46.991318
        neuchatel_lng = 6.926592
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(seconds=5)
        pt1 = LocationPoint(t1, martigny_lat, martigny_lng)
        pt2 = LocationPoint(t2, neuchatel_lat, neuchatel_lng)

        res = estimate_stay_points(
            [pt1, pt2], time_min_ms=4999, distance_max_m=98922.59 - 1
        )
        self.assertTrue(len(res) == 0)

    def test_estimate_stay_points_find_a_point_distance(self):
        martigny_lat = 46.101965
        martigny_lng = 7.079912
        neuchatel_lat = 46.991318
        neuchatel_lng = 6.926592
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(seconds=5)
        pt1 = LocationPoint(t1, martigny_lat, martigny_lng)
        pt2 = LocationPoint(t2, neuchatel_lat, neuchatel_lng)

        res = estimate_stay_points(
            [pt1, pt2], time_min_ms=4999, distance_max_m=99615.43 + 1
        )
        self.assertTrue(len(res) == 1)

    def test_estimate_stay_points_lat_lng(self):
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(seconds=5)
        t3 = t2 + datetime.timedelta(seconds=5)
        pt1 = LocationPoint(t1, 1, 10)
        pt2 = LocationPoint(t2, 2, 20)
        pt3 = LocationPoint(t3, 3, 30)

        res = estimate_stay_points(
            [pt1, pt2, pt3], time_min_ms=4999, distance_max_m=10 ** 17
        )
        self.assertTrue(len(res) == 1)
        res_one = res.pop()
        self.assertAlmostEqual(res_one._lat, 1.5)
        self.assertAlmostEqual(res_one._lng, 15)

    def test_estimate_stay_points_lat_lng_2_points(self):
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(seconds=5)
        t3 = t2 + datetime.timedelta(seconds=5)
        t4 = t3 + datetime.timedelta(seconds=5)
        pt1 = LocationPoint(t1, 1, 10)
        pt2 = LocationPoint(t2, 2, 20)
        pt3 = LocationPoint(t3, 3, 30)
        pt4 = LocationPoint(t4, 4, 40)

        res = estimate_stay_points(
            [pt1, pt2, pt3, pt4], time_min_ms=4999, distance_max_m=10 ** 17
        )
        self.assertTrue(len(res) == 2)
        list_res = sorted(list(res), key=lambda l: l._lat)
        self.assertAlmostEqual(list_res[0]._lat, 1.5)
        self.assertAlmostEqual(list_res[0]._lng, 15)

        self.assertAlmostEqual(list_res[1]._lat, 3.5)
        self.assertAlmostEqual(list_res[1]._lng, 35)

    def test_estimate_stay_points_t_start_t_stop(self):
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(seconds=5)
        t3 = t2 + datetime.timedelta(seconds=5)
        pt1 = LocationPoint(t1, 1, 10)
        pt2 = LocationPoint(t2, 2, 20)
        pt3 = LocationPoint(t3, 3, 30)

        res = estimate_stay_points(
            [pt1, pt2, pt3], time_min_ms=4999, distance_max_m=10 ** 17
        )
        self.assertTrue(len(res) == 1)
        res_one = res.pop()
        self.assertEqual(res_one._t_start, t1)
        self.assertEqual(res_one._t_stop, t2)

    def test_estimate_stay_region_one_day_simple(self):
        current_time = datetime.datetime.now()
        locations = []
        n = 100
        for _ in range(n):
            pt = LocationPoint(current_time, randint(-85, 85), randint(-180, 180))
            locations.append(pt)
            current_time = current_time + datetime.timedelta(seconds=5)

        stay_points = estimate_stay_points(
            locations, time_min_ms=4999, distance_max_m=10 ** 17
        )
        self.assertEqual(len(stay_points), n // 2)
        stay_regions = estimate_stay_regions(stay_points, distance_threshold_m=10 ** 17)

        self.assertEqual(len(stay_regions), 1)

    def test_estimate_stay_region_one_day_2_regions(self):
        current_time = datetime.datetime.now()
        locations = []
        n = 100
        for i in range(n):
            if i < n // 2:
                pt = LocationPoint(current_time, randint(-10, 0), randint(-10, 0))
            else:
                pt = LocationPoint(current_time, randint(50, 55), randint(150, 155))
            locations.append(pt)
            current_time = current_time + datetime.timedelta(seconds=5)

        stay_points = estimate_stay_points(
            locations, time_min_ms=4999, distance_max_m=10 ** 7
        )
        self.assertEqual(len(stay_points), n // 2)
        stay_regions = estimate_stay_regions(stay_points, distance_threshold_m=10 ** 7)

        self.assertEqual(len(stay_regions), 2)

    def test_estimate_stay_region_2x1_region(self):
        day_one = datetime.datetime(2019, 2, 6, 11, 16)
        day_two = datetime.datetime(2019, 2, 7, 11, 16)
        locations = []
        n = 100
        for i in range(n):
            if i < n // 2:
                pt = LocationPoint(day_one, randint(-10, 0), randint(-10, 0))
                day_one = day_one + datetime.timedelta(seconds=5)
            else:
                pt = LocationPoint(day_two, randint(50, 55), randint(150, 155))
                day_two = day_two + datetime.timedelta(seconds=5)
            locations.append(pt)

        stay_points = estimate_stay_points(
            locations, time_min_ms=4999, distance_max_m=10 ** 7
        )
        self.assertEqual(len(stay_points), n // 2)
        stay_regions = estimate_stay_regions_per_day(
            stay_points, distance_threshold_m=10 ** 7
        )

        self.assertEqual(len(stay_regions), 2)

        self.assertEqual(len(stay_regions["2019-02-06"]), 1)
        self.assertEqual(len(stay_regions["2019-02-07"]), 1)

    def test_labelize_stay_region_simple_case(self):
        t1 = datetime.datetime.now()
        t2 = datetime.datetime.now()
        regions = [
            StayRegion(t1, t2, 1.5, 1.5, 2, 2, 1, 1),
            StayRegion(t1, t2, 4.5, 4.5, 5, 5, 4, 4),
        ]
        user_places = [UserPlace(t1, 1.1, 1.1, "one"), UserPlace(t2, 4.1, 4.1, "two")]
        labelled_stay_regions = labelize_stay_region(regions, user_places)
        self.assertEqual(len(labelled_stay_regions), 2)
        one, two = sorted(list(labelled_stay_regions), key=lambda x: x._lat)
        self.assertEqual(one._label, "one")
        self.assertEqual(two._label, "two")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
