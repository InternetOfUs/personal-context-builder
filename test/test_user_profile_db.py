import unittest
from wenet_user_profile_db import set_profile, get_profile, delete_profile


class UserProfileDBTestCase(unittest.TestCase):
    def setUp(self):
        self.user_1 = "user_1"
        self.user_2 = "user_2"

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

    def tearDown(self):
        delete_profile(self.user_1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
