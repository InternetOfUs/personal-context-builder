import unittest
from wenet_data_loading import MockWenetSourceLocations, MockWenetSourceLabels
from wenet_analysis import BagOfWordsVectorizer
from wenet_trainer import BaseBOWTrainer


class BagOfWordsVectorizerTestCase(unittest.TestCase):
    def test_train(self):
        source_locations = MockWenetSourceLocations()
        source_labels = MockWenetSourceLabels(source_locations)
        bow_trainer = BaseBOWTrainer(source_locations, source_labels)
        user_id = source_locations.get_users()[0]
        bow_vectorizer = bow_trainer.train(user_id)
        locations = MockWenetSourceLocations._create_fake_locations(user_id, 20)
        days_locations = BagOfWordsVectorizer.group_by_days(
            locations, user="test_user", start_day="00:00:00", dt_hours=23.5, freq="30T"
        )
        first_day = days_locations[0]
        vector = bow_vectorizer.vectorize(first_day)
        self.assertEqual(sum(vector), 48)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
