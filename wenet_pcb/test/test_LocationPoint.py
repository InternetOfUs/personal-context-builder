import unittest
import datetime
from copy import deepcopy

from regions_builder.models import LocationPoint


class LocationPointTestCase(unittest.TestCase):
    def test_time_difference_ms(self):
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(seconds=1)
        pt1 = LocationPoint(t1, 0, 0)
        pt2 = LocationPoint(t2, 0, 0)
        dt = pt2.time_difference_ms(pt1)
        self.assertEqual(dt, 1000)

    def test_space_distance_m(self):
        martigny_lat = 46.101965
        martigny_lng = 7.079912
        neuchatel_lat = 46.991318
        neuchatel_lng = 6.926592
        t1 = datetime.datetime.now()
        pt1 = LocationPoint(t1, martigny_lat, martigny_lng)
        pt2 = LocationPoint(t1, neuchatel_lat, neuchatel_lng)
        distance = pt1.space_distance_m(pt2)
        distance_truth = 99615.43
        self.assertAlmostEqual(distance, distance_truth, delta=2)

    def test_add(self):
        t1 = datetime.datetime.now()
        pt1 = LocationPoint(t1, 1, 0)
        pt2 = LocationPoint(t1, 0, 1)

        res = pt1 + pt2
        self.assertTrue(res._lat == 1 and res._lng == 1)

    def test_sub(self):
        t1 = datetime.datetime.now()
        pt1 = LocationPoint(t1, 1, 0)
        pt2 = LocationPoint(t1, 0, 1)

        res = pt1 - pt2
        self.assertTrue(res._lat == 1 and res._lng == -1)

    def test_mul(self):
        t1 = datetime.datetime.now()
        pt1 = LocationPoint(t1, 1, 0)
        pt2 = LocationPoint(t1, 0, 1)

        res = pt1 * pt2
        self.assertTrue(res._lat == 0 and res._lng == 0)

    def test_mul_numerical(self):
        t1 = datetime.datetime.now()
        pt1 = LocationPoint(t1, 1, 1)
        res_truth = LocationPoint(t1, 3, 3)

        res = pt1 * 3
        self.assertEqual(res, res_truth)

    def test_truediv(self):
        t1 = datetime.datetime.now()
        pt1 = LocationPoint(t1, 6, 12)
        pt2 = LocationPoint(t1, 2, 3)

        res = pt1 / pt2
        self.assertTrue(res._lat == 3 and res._lng == 4)

    def test_eq(self):
        t1 = datetime.datetime.now()
        pt1 = LocationPoint(t1, 6, 12)
        pt2 = deepcopy(pt1)

        self.assertEqual(pt1, pt2)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
