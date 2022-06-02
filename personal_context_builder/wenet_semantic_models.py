""" module that contains sematic model for the predictions

-  Train on history of the user days with locations and labels
-  Should be able to predict labels probabilities for each time slot for each weekday
-  Should be able to give scores/metrics for validation

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,

"""

from collections import defaultdict
from pprint import pprint
from typing import Dict, List

import numpy as np
from regions_builder.algorithms import estimate_stay_points  # type: ignore
from regions_builder.algorithms import estimate_stay_regions, labelize_stay_region
from regions_builder.data_loading import BaseSourceLabels  # type: ignore
from regions_builder.data_loading import BaseSourceLocations
from regions_builder.models import LabelledStayRegion  # type: ignore
from regions_builder.models import LocationPoint, StayRegion

from personal_context_builder import config
from personal_context_builder.wenet_analysis import BagOfWordsVectorizer, _loads_regions
from personal_context_builder.wenet_exceptions import SemanticRoutinesComputationError
from personal_context_builder.wenet_logger import create_logger
from personal_context_builder.wenet_profile_manager import Label

_LOGGER = create_logger(__name__)


class SemanticModel(object):
    def __init__(
        self,
        locations_source: BaseSourceLocations,
        labels_source: BaseSourceLabels,
        name: str = "unknown_semantic_model",
        regions_mapping_file: str = config.PCB_REGION_MAPPING_FILE,
    ):
        """Constructor
        Args:
            locations_source: source of the locations
            labels_sources: source of the labels
            name: name of the model
        """
        self._locations_source = locations_source
        self._labels_source = labels_source
        self._name = name
        self._regions_mapping = _loads_regions(regions_mapping_file)

    def _compute_indexed_weekday_locations(self, user_id: str):
        locations = self._locations_source.get_locations(user_id)
        if len(locations) == 0:
            raise SemanticRoutinesComputationError(f"no locations for user {user_id}")
        stay_points = estimate_stay_points(locations)
        if len(stay_points) == 0:
            raise SemanticRoutinesComputationError(f"no stay_points for user {user_id}")
        stay_regions = estimate_stay_regions(stay_points)
        if len(stay_regions) == 0:
            raise SemanticRoutinesComputationError(
                f"no stay_regions for user {user_id}"
            )
        user_places = self._labels_source.get_labels(user_id)
        if len(user_places) == 0:
            raise SemanticRoutinesComputationError(f"no user_places for user {user_id}")
        labelled_stay_regions = labelize_stay_region(
            stay_regions, user_places, fill_unknown=config.PCB_FILL_UNKNOWN
        )
        if len(labelled_stay_regions) == 0:
            raise SemanticRoutinesComputationError(
                f"no labelled_stay_regions for user {user_id}"
            )
        stay_regions = list(set(stay_regions) - set(labelled_stay_regions))
        all_days_locations = BagOfWordsVectorizer.group_by_days(locations, user_id)
        indexed_weekday_locations = self.index_per_weekday(all_days_locations)
        return indexed_weekday_locations, labelled_stay_regions, stay_regions

    def compute_labels_for_user(self, user_id: str):
        """Compute the labels for a given user
        Args:
            user_id: for which user

        TODO user specific location for labels

        Returns: dict of semantic labels with Label
        """
        res = dict(
            [
                (semantic_id, Label(label_name, semantic_id, 0, 0))
                for label_name, semantic_id in self._regions_mapping.items()
            ]
        )
        return res

    def compute_weekdays(self, user_id: str):
        """Compute the all weekday distributions for the given user
        Args:
            user_id: for which user the weekday are computed

        Return: Distribution of the labels for each day for each time slots
        """
        raise NotImplementedError("not implemented")

    def evaluate_user(self, user_id: str):
        """Score the models for user_id"""

    def evaluate_all(self):
        """Score the models for all users"""

    @classmethod
    def index_per_weekday(
        cls, all_days_locations: List[LocationPoint]
    ) -> Dict[int, List[LocationPoint]]:
        """group all days by weekday and use weekday as index
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
    def compute_weekdays(self, user_id: str):
        (
            indexed_weekday_locations,
            labelled_stay_regions,
            stay_regions,
        ) = self._compute_indexed_weekday_locations(user_id)
        labels_count: Dict[int, Dict[str, Dict[str, float]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: 0))
        )
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

    def _compute_labels_dist(
        self, labels_count: Dict[int, Dict[str, Dict[str, float]]]
    ):
        """compute the distribution of the labels for each timeslots grouped per weekday
        Args:
            labels_count: hierarchical labels count (dict of dict of dict)
        """
        labels_dist: Dict[int, Dict[str, Dict[str, float]]] = defaultdict(
            lambda: defaultdict(lambda: dict())
        )
        for weekday, time_labels_freq in labels_count.items():
            for time_slot, labels_freq in time_labels_freq.items():
                nb_items = sum(labels_freq.values())
                for label, nb in labels_freq.items():
                    labels_dist[weekday][time_slot][label] = nb / nb_items
        return labels_dist

    def _fill_with_labels_count(
        self,
        location: LocationPoint,
        labels_count: Dict[int, Dict[str, Dict[str, float]]],
        weekday: int,
        labelled_stay_regions: List[LabelledStayRegion],
        stay_regions: List[StayRegion],
    ):
        """determine the labels and fill hierarchically labels_count with
            the number of each labels per timeslot per weekday
        Args:
            location: location point to check
            labels_count: hierarchical labels count (dict of dict of dict)
            weekday: day of the week (number)
            labelled_stay_regions: the labelled stay regions
            stay_regions: the unlabelled stay regions
        """
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
                        label = self._regions_mapping["unknown_labelled_region"]
                    labels_count[weekday][location._pts_t.strftime("%H:%M:%S")][
                        label
                    ] += 1
                    is_in_region = True
                    break
            for region in stay_regions:
                if location in region:
                    labels_count[weekday][location._pts_t.strftime("%H:%M:%S")][
                        self._regions_mapping["unknown_region"]
                    ] += 1
                    is_in_region = True
                    break
            if not is_in_region:
                labels_count[weekday][location._pts_t.strftime("%H:%M:%S")][
                    self._regions_mapping["unknown"]
                ] += 1
