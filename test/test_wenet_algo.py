import unittest
import datetime
from copy import deepcopy

from wenet_models import LocationPoint
from wenet_algo import estimate_centroid, estimate_stay_points


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
            [pt1, pt2], time_min_ms=4999, distance_max_m=98922.59 + 1
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


if __name__ == "__main__":
    unittest.main()
