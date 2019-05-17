from wenet_analysis import BagOfWordsVectorizer
from wenet_data_loading import MockWenetSourceLocations
import unittest


class BagOfWordsVectorizerTestCase(unittest.TestCase):
    def test_group_by_days(self):
        locations = MockWenetSourceLocations._create_fake_locations("test_user", 10)
        days_locations = BagOfWordsVectorizer.group_by_days(
            locations, user="test_user", start_day="00:00:00", dt_hours=23.5, freq="30T"
        )
        first_day = days_locations[0]
        self.assertEqual(len(first_day), 48)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
