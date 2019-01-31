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

    def test_space_distance_m(self):
        martigny_lat = 46.101965
        martigny_lng = 7.079912
        neuchatel_lat = 46.991318
        neuchatel_lng = 6.926592
        t1 = datetime.datetime.now()
        pt1 = LocationPoint(t1, martigny_lat, martigny_lng)
        pt2 = LocationPoint(t1, neuchatel_lat, neuchatel_lng)
        distance = pt1.space_distance_m(pt2)
        distance_truth = 98922.59
        self.assertAlmostEqual(distance, distance_truth, delta=2)

    def test_add(self):
        t1 = datetime.datetime.now()
        pt1 = LocationPoint(t1, 1, 0)
        pt2 = LocationPoint(t1, 0, 1)

        res = pt1 + pt2
        self.assertTrue(res._lat == 1 and res._lng == 1)


if __name__ == "__main__":
    unittest.main()
