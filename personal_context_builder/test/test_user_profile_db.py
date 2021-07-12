""" Test for the user profiles db

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,
"""

import unittest

from personal_context_builder.wenet_user_profile_db import (
    DatabaseProfileHandlerMock,
    DatabaseProfileHandler,
)


class UserProfileDBTestCase(unittest.TestCase):
    def setUp(self):
        self.user_1 = "user_1"
        self.user_2 = "user_2"
        self.user_3 = "user_3"
        self.user_4 = "user_4"
        self.user_5 = "test_user_5"
        self.user_6 = "test_user_6"

    def test_create_retreive_user(self):
        user_vector = [0, 1, 1, 0, 1, 0.5]
        DatabaseProfileHandlerMock.get_instance().set_profile(self.user_1, user_vector)
        res = DatabaseProfileHandlerMock.get_instance().get_profile(self.user_1)
        self.assertEqual(user_vector, res)

    def test_delete_user(self):
        user_vector = [1, 0.5, 1, 0, 0, 0]
        DatabaseProfileHandlerMock.get_instance().set_profile(self.user_2, user_vector)
        DatabaseProfileHandlerMock.get_instance().delete_profile(self.user_2)
        res = DatabaseProfileHandlerMock.get_instance().get_profile(self.user_2)
        self.assertIsNone(res)

    def test_set_profiles(self):
        v1 = [0, 1, 0, 1]
        v2 = [1, 0, 1, 0]
        DatabaseProfileHandlerMock.get_instance().set_profiles(
            [self.user_3, self.user_4], [v1, v2]
        )
        res = DatabaseProfileHandlerMock.get_instance().get_profile(self.user_4)
        self.assertEqual(v2, res)

    def test_get_all_profiles(self):
        v1 = [0, 1, 0, 1]
        v2 = [1, 0, 1, 0]
        DatabaseProfileHandlerMock.get_instance().set_profiles(
            [self.user_5, self.user_6], [v1, v2]
        )
        res = DatabaseProfileHandlerMock.get_instance().get_all_profiles(match="test_*")
        self.assertEqual(v2, res[self.user_6])

    def tearDown(self):
        DatabaseProfileHandlerMock.get_instance().delete_profile(self.user_1)
        #  2 is deleted in another testcase
        DatabaseProfileHandlerMock.get_instance().delete_profile(self.user_3)
        DatabaseProfileHandlerMock.get_instance().delete_profile(self.user_4)
        DatabaseProfileHandlerMock.get_instance().delete_profile(self.user_5)
        DatabaseProfileHandlerMock.get_instance().delete_profile(self.user_6)


class UserProfileDBRealTestCase(unittest.TestCase):
    def setUp(self):
        self.user_1 = "user_1"
        self.user_2 = "user_2"
        self.user_3 = "user_3"
        self.user_4 = "user_4"
        self.user_5 = "test_user_5"
        self.user_6 = "test_user_6"

    def test_create_retreive_user(self):
        user_vector = [0, 1, 1, 0, 1, 0.5]
        DatabaseProfileHandler.get_instance().set_profile(self.user_1, user_vector)
        res = DatabaseProfileHandler.get_instance().get_profile(self.user_1)
        self.assertEqual(user_vector, res)

    def test_delete_user(self):
        user_vector = [1, 0.5, 1, 0, 0, 0]
        DatabaseProfileHandler.get_instance().set_profile(self.user_2, user_vector)
        DatabaseProfileHandler.get_instance().delete_profile(self.user_2)
        res = DatabaseProfileHandler.get_instance().get_profile(self.user_2)
        self.assertIsNone(res)

    def test_set_profiles(self):
        v1 = [0, 1, 0, 1]
        v2 = [1, 0, 1, 0]
        DatabaseProfileHandler.get_instance().set_profiles(
            [self.user_3, self.user_4], [v1, v2]
        )
        res = DatabaseProfileHandler.get_instance().get_profile(self.user_4)
        self.assertEqual(v2, res)

    def test_get_all_profiles(self):
        v1 = [0, 1, 0, 1]
        v2 = [1, 0, 1, 0]
        DatabaseProfileHandler.get_instance().set_profiles(
            [self.user_5, self.user_6], [v1, v2]
        )
        res = DatabaseProfileHandler.get_instance().get_all_profiles(match="test_*")
        self.assertEqual(v2, res[self.user_6])

    def tearDown(self):
        DatabaseProfileHandler.get_instance().delete_profile(self.user_1)
        #  2 is deleted in another testcase
        DatabaseProfileHandler.get_instance().delete_profile(self.user_3)
        DatabaseProfileHandler.get_instance().delete_profile(self.user_4)
        DatabaseProfileHandler.get_instance().delete_profile(self.user_5)
        DatabaseProfileHandler.get_instance().delete_profile(self.user_6)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
