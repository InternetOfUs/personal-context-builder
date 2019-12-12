import unittest
import datetime

from regions_builder.models import UserPlace


class UserPlaceTestCase(unittest.TestCase):
    def test_constructor(self):
        t1 = datetime.datetime.now()
        up = UserPlace(t1, 1, 0, "test", user="toto")
        self.assertEqual(up._label, "test")
        self.assertEqual(up._user, "toto")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
