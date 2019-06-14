import unittest
import datetime

from wenet_pcb.wenet_models import UserPlaceTimeOnly, LocationPoint, StayPoint


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

    def test_to_user_place_from_stay_points_return_none(self):
        pts_t = datetime.datetime(2019, 2, 8, 8, 30)
        pts_t_2 = datetime.datetime(2019, 2, 8, 19, 30)

        pts_t_place = datetime.datetime(2019, 2, 8, 22, 30)

        stay_point = StayPoint(pts_t, pts_t_2, 1, 1)

        place_time_only = UserPlaceTimeOnly(pts_t_place, "bar")
        place = place_time_only.to_user_place_from_stay_points(
            [stay_point], max_delta_time_ms=60 * 60 * 1000
        )
        self.assertIsNone(place)

    def test_to_user_place_from_stay_points_good_place(self):
        pts_t = datetime.datetime(2019, 2, 8, 8, 30)
        pts_t_2 = datetime.datetime(2019, 2, 8, 19, 30)

        pts_t_place = datetime.datetime(2019, 2, 8, 12, 30)

        stay_point = StayPoint(pts_t, pts_t_2, 1, 1)

        place_time_only = UserPlaceTimeOnly(pts_t_place, "bar")
        place = place_time_only.to_user_place_from_stay_points(
            [stay_point], max_delta_time_ms=60 * 60 * 1000
        )
        self.assertIsNotNone(place)
        self.assertEqual(place._lat, 1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
