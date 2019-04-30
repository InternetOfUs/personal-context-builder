"""
Module that load locations/labels data
"""

from abc import ABC, abstractmethod


class BaseSourceLocations(ABC):
    def __init__(self, name):
        self._name = name

    @abstractmethod
    def get_users(self):
        pass

    @abstractmethod
    def get_locations(self, user_id, max_n=None):
        pass

    @abstractmethod
    def get_locations_all_users(self, max_n=None):
        pass


class BaseSourceLabels(ABC):
    def __init__(self, name):
        self._name = name

    @abstractmethod
    def get_users(self):
        pass

    @abstractmethod
    def get_labels(self, user_id, max_n=None):
        pass

    @abstractmethod
    def get_labels_all_users(self, max_n=None):
        pass
