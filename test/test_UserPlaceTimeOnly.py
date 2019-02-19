import unittest
import datetime

from wenet_models import UserPlaceTimeOnly, LocationPoint


class UserPlaceTimeOnlyTestCase(unittest.TestCase):
    def test_to_user_place_return_none(self):
        pts_t = datetime.datetime(2019, 2, 8, 8, 30)
        pts_t_late = datetime.datetime(2019, 2, 8, 9, 30)
        locations = [LocationPoint(pts_t_late, 1, 1)]

        place_time_only = UserPlaceTimeOnly(pts_t, "bar")
        place = place_time_only.to_user_place(
            locations,
            max_delta_time_ms=(abs((pts_t_late - pts_t).total_seconds()) - 2) * 1000,
        )
        self.assertIsNone(place)

    def test_to_user_place_return_good_place(self):
        pts_t = datetime.datetime(2019, 2, 8, 8, 30)
        pts_t_late = datetime.datetime(2019, 2, 8, 9, 30)
        locations = [LocationPoint(pts_t_late, 1, 1)]

        place_time_only = UserPlaceTimeOnly(pts_t, "bar")
        place = place_time_only.to_user_place(
            locations,
            max_delta_time_ms=(abs((pts_t_late - pts_t).total_seconds()) + 2) * 1000,
        )
        self.assertIsNotNone(place)
        self.assertEqual(place._lat, locations[0]._lat)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
