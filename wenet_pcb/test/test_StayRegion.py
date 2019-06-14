import unittest
import datetime

from wenet_pcb.wenet_models import StayRegion, GPSPoint


class StayRegionTestCase(unittest.TestCase):
    def test_in(self):
        t1 = datetime.datetime.now()
        t2 = datetime.datetime.now()
        region = StayRegion(t1, t2, 1.5, 1.5, 2, 2, 1, 1)
        point_inside = GPSPoint(1.1, 1.1)
        point_outside = GPSPoint(2.1, 2.1)
        self.assertIn(point_inside, region)
        self.assertNotIn(point_outside, region)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
