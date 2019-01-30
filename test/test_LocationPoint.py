import unittest
import datetime

from wenet_models import LocationPoint


class LocationPointTestCase(unittest.TestCase):
    def test_time_difference_ms(self):
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(seconds=1)
        pt1 = LocationPoint(t1, 0, 0)
        pt2 = LocationPoint(t2, 0, 0)
        dt = pt2.time_difference_ms(pt1)
        self.assertEqual(dt, 1000)


if __name__ == "__main__":
    unittest.main()
