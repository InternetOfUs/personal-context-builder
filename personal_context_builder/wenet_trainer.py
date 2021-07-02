""" module to train models

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,

"""

import numpy as np
from regions_builder.algorithms import (
    estimate_stay_points,
    estimate_stay_regions,
    labelize_stay_region,
)

from personal_context_builder import config
from personal_context_builder.wenet_analysis import (
    BagOfWordsCorpuzer,
    BagOfWordsVectorizer,
)


class BaseModelTrainer(object):
    def __init__(
        self, locations_source, labels_source, bow_trainer, untrained_model_instance
    ):
        """Handle the training of models
        Args:
            locations_source: source of data of locations
            labels_source: source of data for the labels
            bow_trainer: Bag-of-words trainer to use
            untrained_model_instance: the instance to train
        """
        self._locations_source = locations_source
        self._labels_source = labels_source
        self._bow_trainer = bow_trainer
        self._untrained_model_instance = untrained_model_instance

    def train(self):
        """Train to untrained_model_instance using bow_trainer
        Return:
            trained instance of the model
        """
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
        """Handle the trainer of the Bag-Of-Words
        Args:
            locations_source: source of data of locations
            labels_source: source of data for the labels
            regions_mapping_file: region mapping file to use
        """
        self._locations_source = locations_source
        self._labels_source = labels_source
        self._regions_mapping_file = regions_mapping_file

    def train(self, user_id):
        """train by using this user_id
        Args:
            user_id: user to use to train
        Return:
            Trained bow vectorizer
        """
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
        """Vectorize the data for all users, for all days
        Return:
            2D array with data or None if zero data
        """
        data = []
        cpt = 0
        for (
            user_id,
            locations,
        ) in self._locations_source.get_locations_all_users().items():
            bow_vectorizer = self.train(user_id)
            for day in BagOfWordsVectorizer.group_by_days(locations, user_id):
                X = bow_vectorizer.vectorize(day)
                data += X
                cpt += 1
        if cpt > 0:
            return np.array(data).reshape(cpt, -1)
        else:
            return None


class HDPTrainer(BaseBOWTrainer):
    def __init__(
        self,
        locations_source,
        labels_source,
        regions_mapping_file=config.DEFAULT_REGION_MAPPING_FILE,
    ):
        """Handle the trainer of the HDP
        Args:
            locations_source: source of data of locations
            labels_source: source of data for the labels
            regions_mapping_file: region mapping file to use
        """
        super().__init__(
            locations_source,
            labels_source,
            regions_mapping_file=config.DEFAULT_REGION_MAPPING_FILE,
        )

    def train(self, user_id):
        """train by using this user_id
        Args:
            user_id: user to use to train
        Return:
            Trained bow vectorizer
        """
        stay_points = estimate_stay_points(
            self._locations_source.get_locations(user_id)
        )
        stay_regions = estimate_stay_regions(stay_points)
        user_places = self._labels_source.get_labels(user_id)
        labelled_stay_regions = labelize_stay_region(stay_regions, user_places)
        stay_regions = list(set(stay_regions) - set(labelled_stay_regions))
        bow_vectorizer = BagOfWordsCorpuzer(
            labelled_stay_regions, stay_regions, self._regions_mapping_file
        )
        return bow_vectorizer

    def vectorize(self):
        """Vectorize the data for all users, for all days
        Return:
            2D array with data or None if zero data
        """
        data = []
        cpt = 0
        for (
            user_id,
            locations,
        ) in self._locations_source.get_locations_all_users().items():
            bow_vectorizer = self.train(user_id)
            for day in BagOfWordsVectorizer.group_by_days(locations, user_id):
                X = bow_vectorizer.vectorize(day)
                data += X
                cpt += 1
        if cpt > 0:
            return np.array(data).reshape(cpt, -1)
        else:
            return None
