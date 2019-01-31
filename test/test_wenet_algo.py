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


if __name__ == "__main__":
    unittest.main()
