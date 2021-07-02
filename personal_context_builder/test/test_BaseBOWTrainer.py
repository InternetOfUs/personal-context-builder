""" Test for the bag of words trainer

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,
"""

import unittest

from regions_builder.data_loading import MockWenetSourceLabels, MockWenetSourceLocations

from personal_context_builder import config
from personal_context_builder.wenet_analysis import BagOfWordsVectorizer, _loads_regions
from personal_context_builder.wenet_trainer import BaseBOWTrainer


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

    def test_vectorize(self):
        source_locations = MockWenetSourceLocations(nb=20)
        source_labels = MockWenetSourceLabels(source_locations)
        bow_trainer = BaseBOWTrainer(source_locations, source_labels)
        nb_users = len(source_locations.get_users())
        vectors = bow_trainer.vectorize()
        vectors_size = (
            max(list(_loads_regions(config.DEFAULT_REGION_MAPPING_FILE).values())) * 48
        )
        self.assertEqual(vectors.shape, (nb_users, vectors_size))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
