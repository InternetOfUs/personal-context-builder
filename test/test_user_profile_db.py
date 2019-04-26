import unittest
from wenet_user_profile_db import set_profile, get_profile, delete_profile, set_profiles


class UserProfileDBTestCase(unittest.TestCase):
    def setUp(self):
        self.user_1 = "user_1"
        self.user_2 = "user_2"
        self.user_3 = "user_3"
        self.user_4 = "user_4"

    def test_create_retreive_user(self):
        user_vector = [0, 1, 1, 0, 1, 0.5]
        set_profile(self.user_1, user_vector)
        res = get_profile(self.user_1)
        self.assertEqual(user_vector, res)

    def test_delete_user(self):
        user_vector = [1, 0.5, 1, 0, 0, 0]
        set_profile(self.user_2, user_vector)
        delete_profile(self.user_2)
        res = get_profile(self.user_2)
        self.assertIsNone(res)

    def test_set_profiles(self):
        v1 = [0, 1, 0, 1]
        v2 = [1, 0, 1, 0]
        set_profiles([self.user_3, self.user_4], [v1, v2])
        res = get_profile(self.user_4)
        self.assertEqual(v2, res)

    def tearDown(self):
        delete_profile(self.user_1)
        #  2 is deleted in another testcase
        delete_profile(self.user_3)
        delete_profile(self.user_4)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
