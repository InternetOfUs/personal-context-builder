""" module that contains sematic model for the predictions

-  Train on history of the user days with locations and labels
-  Should be able to predict labels probabilities for each time slot for each weekday
-  Should be able to give scores/metrics for validation
"""

from collections import defaultdict
import numpy as np

from wenet_pcb.wenet_algo import (
    estimate_stay_points,
    estimate_stay_regions,
    labelize_stay_region,
)

from wenet_pcb.wenet_analysis import _loads_regions, BagOfWordsVectorizer
from wenet_pcb import config
from pprint import pprint


class SemanticModel(object):
    def __init__(
        self,
        locations_source,
        labels_source,
        name="unknown_semantic_model",
        regions_mapping_file=config.DEFAULT_REGION_MAPPING_FILE,
    ):
        """ Constructor
        Args:
            locations_source: source of the locations
            labels_sources: source of the labels
            name: name of the model
        """
        self._locations_source = locations_source
        self._labels_source = labels_source
        self._name = name
        self._regions_mapping = _loads_regions(regions_mapping_file)

    def _compute_indexed_weekday_locations(self, user_id):
        locations = self._locations_source.get_locations(user_id)
        stay_points = estimate_stay_points(locations)
        stay_regions = estimate_stay_regions(stay_points)
        user_places = self._labels_source.get_labels(user_id)
        labelled_stay_regions = labelize_stay_region(stay_regions, user_places)
        stay_regions = list(set(stay_regions) - set(labelled_stay_regions))
        all_days_locations = BagOfWordsVectorizer.group_by_days(locations, user_id)
        indexed_weekday_locations = self.index_per_weekday(all_days_locations)
        return indexed_weekday_locations, labelled_stay_regions, stay_regions

    def compute_weekdays(self, user_id):
        """ Compute the all weekday distributions for the given user
        Args:
            user_id: for which user the weekday are computed

        Return: Distribution of the labels for each day for each time slots
        """
        raise NotImplementedError("not implemented")

    def evaluate_user(self, user_id):
        """ Score the models for user_id
        """
        pass

    def evaluate_all(self):
        """ Score the models for all users
        """
        pass

    @classmethod
    def index_per_weekday(cls, all_days_locations):
        """ group all days by weekday and use weekday as index
        Args:
            all_days_locations: list of list of locations, sublist are full day

        Return: indexed days of locations
        """
        res = defaultdict(list)
        for locations_day in all_days_locations:
            middle_location = locations_day[len(locations_day) // 2]
            weekday = middle_location._pts_t.weekday()
            res[weekday].append(locations_day)
        return res


class SemanticModelHist(SemanticModel):
    def compute_weekdays(self, user_id):
        indexed_weekday_locations, labelled_stay_regions, stay_regions = self._compute_indexed_weekday_locations(
            user_id
        )
        labels_count = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))
        for weekday, days_locations in indexed_weekday_locations.items():
            for day_locations in days_locations:
                for location in day_locations:
                    self._fill_with_labels_count(
                        location,
                        labels_count,
                        weekday,
                        labelled_stay_regions,
                        stay_regions,
                    )
        labels_dist = self._compute_labels_dist(labels_count)

        return labels_dist

    def _compute_labels_dist(self, labels_count):
        labels_dist = defaultdict(lambda: defaultdict(lambda: dict()))
        for weekday, time_labels_freq in labels_count.items():
            for time_slot, labels_freq in time_labels_freq.items():
                nb_items = sum(labels_freq.values())
                for label, nb in labels_freq.items():
                    labels_dist[weekday][time_slot][label] = nb / nb_items
        return labels_dist

    def _fill_with_labels_count(
        self, location, labels_count, weekday, labelled_stay_regions, stay_regions
    ):
        if location is None or np.isnan(location._lat):
            labels_count[weekday][location._pts_t.strftime("%H:%M:%S")][
                self._regions_mapping["no_data"]
            ] += 1
        else:
            is_in_region = False
            for region in labelled_stay_regions:
                if location in region:
                    if region._label in self._regions_mapping:
                        label = self._regions_mapping[region._label]
                    else:
                        label = self._regions_mapping["unknow_labelled_region"]
                    labels_count[weekday][location._pts_t.strftime("%H:%M:%S")][
                        label
                    ] += 1
                    is_in_region = True
                    break
            for region in stay_regions:
                if location in region:
                    labels_count[weekday][location._pts_t.strftime("%H:%M:%S")][
                        self._regions_mapping["unknow_region"]
                    ] += 1
                    is_in_region = True
                    break
            if not is_in_region:
                labels_count[weekday][location._pts_t.strftime("%H:%M:%S")][
                    self._regions_mapping["unknow"]
                ] += 1
