""" module to train models
"""

from wenet_analysis import BagOfWordsVectorizer
from wenet_algo import estimate_stay_points, estimate_stay_regions, labelize_stay_region
import config
import numpy as np


class BaseModelTrainer(object):
    def __init__(
        self, locations_source, labels_source, bow_trainer, untrained_model_instance
    ):
        self._locations_source = locations_source
        self._labels_source = labels_source
        self._bow_trainer = bow_trainer
        self._untrained_model_instance = untrained_model_instance

    def train(self):
        X = self._bow_trainer.vectorize()
        self._untrained_model_instance.fit(X)
        return self._untrained_model_instance


class BaseBOWTrainer(object):
    def __init__(
        self,
        locations_source,
        labels_source,
        regions_mapping_file=config.DEFAULT_REGION_MAPPING_FILE,
    ):
        self._locations_source = locations_source
        self._labels_source = labels_source
        self._regions_mapping_file = regions_mapping_file

    def train(self, user_id):
        stay_points = estimate_stay_points(
            self._locations_source.get_locations(user_id)
        )
        stay_regions = estimate_stay_regions(stay_points)
        user_places = self._labels_source.get_labels(user_id)
        labelled_stay_regions = labelize_stay_region(stay_regions, user_places)
        stay_regions = list(set(stay_regions) - set(labelled_stay_regions))
        bow_vectorizer = BagOfWordsVectorizer(
            labelled_stay_regions, stay_regions, self._regions_mapping_file
        )
        return bow_vectorizer

    def vectorize(self):
        data = []
        len_data = 0
        for (
            user_id,
            locations,
        ) in self._locations_source.get_locations_all_users().items():
            bow_vectorizer = self.train(user_id)
            for day in BagOfWordsVectorizer.group_by_days(locations, user_id):
                X = bow_vectorizer.vectorize(day)
                data += X
        len_data = len(data)
        if len_data > 0:
            return np.array(data).reshape(len_data, -1)
        else:
            return None

