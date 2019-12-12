import unittest
import datetime
from copy import deepcopy

from regions_builder.models import StayPoint
from regions_builder.tools import space_distance_m


class StayPointTestCase(unittest.TestCase):
    def test_eq(self):
        t1 = datetime.datetime.now()
        t2 = datetime.datetime.now()
        pt1 = StayPoint(t1, t2, 25, 30)
        pt2 = deepcopy(pt1)

        self.assertEqual(pt1, pt2)

    def test_min_max_latitude(self):
        t1 = datetime.datetime.now()
        t2 = datetime.datetime.now()
        pt1 = StayPoint(t1, t2, 25, 30, accuracy_m=20)
        min_lat, max_lat = pt1._get_min_max_latitude_from_accuracy(delta_inc=0.000001)
        distance = space_distance_m(min_lat, 30, max_lat, 30)
        self.assertAlmostEqual(distance, 40, delta=1)

    def test_min_max_longitude(self):
        t1 = datetime.datetime.now()
        t2 = datetime.datetime.now()
        pt1 = StayPoint(t1, t2, 25, 30, accuracy_m=20)
        min_lng, max_lng = pt1._get_min_max_longitude_from_accuracy(delta_inc=0.000001)
        distance = space_distance_m(25, min_lng, 25, max_lng)
        self.assertAlmostEqual(distance, 40, delta=1)

    def test_get_surrounded_points(self):
        t1 = datetime.datetime.now()
        t2 = datetime.datetime.now()
        pt1 = StayPoint(t1, t2, 25, 30, accuracy_m=20)
        points = pt1._get_surrouder_points(delta_inc=0.0000001)

        self.assertEqual(len(points), 100)

        greater_points = [p for p in points if p.space_distance_m(pt1) > 22]
        self.assertEqual(len(greater_points), 0)
        lesser_points = [p for p in points if p.space_distance_m(pt1) < 18]
        self.assertEqual(len(lesser_points), 0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
