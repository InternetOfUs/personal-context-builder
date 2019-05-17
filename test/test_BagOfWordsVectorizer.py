from wenet_analysis import BagOfWordsVectorizer
from wenet_data_loading import MockWenetSourceLocations, MockWenetSourceLabels
import unittest
from os import remove


class BagOfWordsVectorizerTestCase(unittest.TestCase):
    def test_save_load(self):
        source_locations = MockWenetSourceLocations()
        source_labels = MockWenetSourceLabels(source_locations)
        vectorizer = BagOfWordsVectorizer(source_locations, source_labels)
        regions_size = vectorizer._inner_vector_size
        filename = "bow_delete_me.p"
        vectorizer.save(filename)
        vectorizer = BagOfWordsVectorizer.load(filename)
        remove(filename)
        self.assertEqual(regions_size, vectorizer._inner_vector_size)

    def test_group_by_days(self):
        locations = MockWenetSourceLocations._create_fake_locations("test_user", 10)
        days_locations = BagOfWordsVectorizer.group_by_days(
            locations, user="test_user", start_day="00:00:00", dt_hours=23.5, freq="30T"
        )
        first_day = days_locations[0]
        self.assertEqual(len(first_day), 48)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
