import unittest
import datetime
from copy import deepcopy

from wenet_models import LocationPoint
from wenet_algo import estimate_centroid


class WenetAlgoTestCase(unittest.TestCase):
    def test_estimate_centroid(self):
        t1 = datetime.datetime.now()
        pt1 = LocationPoint(t1, 0, 0)
        pt2 = LocationPoint(t1, 1, 1)
        pt3 = LocationPoint(t1, 2, 2)

        res = estimate_centroid([pt1, pt2, pt3])
        self.assertTrue(res._lat == 1 and res._lng == 1)


if __name__ == "__main__":
    unittest.main()
