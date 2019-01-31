import unittest
import datetime
from copy import deepcopy

from wenet_models import StayPoint


class StayPointTestCase(unittest.TestCase):
    def test_eq(self):
        t1 = datetime.datetime.now()
        t2 = datetime.datetime.now()
        pt1 = StayPoint(t1, t2, 25, 30)
        pt2 = deepcopy(pt1)

        self.assertEqual(pt1, pt2)


if __name__ == "__main__":
    unittest.main()
