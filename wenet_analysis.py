"""
module that analyse user's routines
"""
import config
import json
import numpy as np
from copy import deepcopy
from functools import lru_cache
import pickle


@lru_cache(maxsize=None)
def _loads_regions(regions_mapping_file):
    """ loads regions mapping file

    this function is cached to avoid unnecessary disk accesses

    Args:
        regions_mapping_file: the filename where the json mapping file is

    Return:
        dict created from the json file
    """
    with open(regions_mapping_file, "r") as f:
        return json.load(f)


class BagOfWordsVectorizer(object):
    def __init__(
        self,
        labelled_stay_regions,
        stay_regions,
        regions_mapping_file=config.DEFAULT_REGION_MAPPING_FILE,
    ):
        self._labelled_stay_regions = labelled_stay_regions
        self._stay_regions = stay_regions
        self._regions_mapping = _loads_regions(regions_mapping_file)
        self._inner_vector_size = max(self._regions_mapping.values()) + 1

    def vectorize(self, locations):
        """ Create a bag of words vector
        Args:
            locations: list of LocationPoint

        Return:
            vector (list of floats)
        """
        big_vector = []
        inner_vector = [0] * self._inner_vector_size
        for location in locations:
            current_vector = deepcopy(inner_vector)
            if location is None or np.isnan(location._lat):
                current_vector[self._regions_mapping["no_data"]] = 1
            else:
                is_in_region = False
                for region in self._labelled_stay_regions:
                    if location in region:
                        current_vector[self._regions_mapping[region._label]] = 1
                        is_in_region = True
                        break
                for region in self._stay_regions:
                    if location in region:
                        current_vector[self._regions_mapping["unknow_region"]] = 1
                        is_in_region = True
                        break
                if not is_in_region:
                    current_vector[self._regions_mapping["unknow"]] = 1
            big_vector += current_vector
        return big_vector

    def save(self, filename=config.DEFAULT_BOW_MODEL_FILE, dump_fct=pickle.dump):
        """ save this current instance of BagOfWordsVectorizer
            Args:
                filename: file that will be used to store the instance
                dump_fct: function to use to dump the instance into a file
        """
        with open(filename, "wb") as f:
            dump_fct(self.__dict__, f)

    @staticmethod
    def load(filename=config.DEFAULT_BOW_MODEL_FILE, load_fct=pickle.load):
        """ Create a instance of BagOfWordsVectorizer from a previously saved file
            Args:
                filename: file that contain the saved BagOfWordsVectorizer instance
                load_fct: function to use to load the instance from a file
            Return:
                An instance of BagOfWordsVectorizer
        """
        with open(filename, "rb") as f:
            instance = BagOfWordsVectorizer(None, None)
            instance.__dict__ = load_fct(f)
            return instance
