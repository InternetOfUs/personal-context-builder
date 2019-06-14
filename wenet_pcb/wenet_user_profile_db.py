"""
Module that handle database access for user's profile

TODO refactor to use class, for make it easier to mock and test
"""
from wenet_pcb import config
import redis
import json
from abc import ABC, abstractmethod
from sanic.exceptions import ServerError
from wenet_pcb.wenet_logger import create_logger

_LOGGER = create_logger(__name__)


class DatabaseProfileHandlerBase(ABC):
    """ Base interface for handling database access for the profiles

    is a dict of Singleton
    """

    _INSTANCES = dict()

    @classmethod
    def get_instance(cls, *args, db_index=0, **kwargs):
        if db_index not in cls._INSTANCES:
            cls._INSTANCES[db_index] = cls(*args, db_index=db_index, **kwargs)
        return cls._INSTANCES[db_index]

    @abstractmethod
    def clean_db(self):
        pass

    @abstractmethod
    def delete_profile(self, user_id):
        pass

    @abstractmethod
    def get_all_profiles(self, match=None):
        pass

    @abstractmethod
    def get_profile(self, user_id):
        pass

    @abstractmethod
    def set_profile(self, user_id, vector):
        pass

    @abstractmethod
    def set_profiles(self, user_ids, vectors):
        pass


class DatabaseProfileHandlerMock(DatabaseProfileHandlerBase):
    def __init__(self, db_index=0):
        self._my_dict = dict()

    def clean_db(self):
        _LOGGER.info("mock clean db called")
        self._my_dict = dict()

    def delete_profile(self, user_id):
        _LOGGER.info(f"mock delete profile {user_id}")
        try:
            del self._my_dict[user_id]
        except KeyError:
            pass

    def get_all_profiles(self, match=None):
        _LOGGER.info("mock get all profiles")
        return self._my_dict

    def get_profile(self, user_id):
        _LOGGER.info(f"mock get profile {user_id}")
        try:
            return self._my_dict[user_id]
        except KeyError:
            _LOGGER.warn(f"\tmock unable to get profile {user_id} - doesn't exist")
            return None

    def set_profile(self, user_id, vector):
        _LOGGER.info(f"mock set profile {user_id} with {vector}")
        self._my_dict[user_id] = vector

    def set_profiles(self, user_ids, vectors):
        for user_id, vector in zip(user_ids, vectors):
            self.set_profile(user_id, vector)


class DatabaseProfileHandler(DatabaseProfileHandlerBase):
    """ Handle database to the redis server

    Not thread safe

    """

    def __init__(
        self, db_index=0, host=config.DEFAULT_REDIS_HOST, port=config.DEFAULT_REDIS_PORT
    ):
        self._server = redis.Redis(host=host, port=port, db=db_index)
        try:
            self._server.ping()
        except:  # TODO catch specific exception
            raise ServerError("Unable to access the Redis DB")

    def clean_db(self):
        """ clean the db (delete all entries)
        """
        _LOGGER.info("clean db called")
        for key in self._server.scan_iter():
            self._server.delete(key)

    def delete_profile(self, user_id):
        """ delete a profile
        Args:
            user_id: user_id of the profile
        """
        _LOGGER.info(f"delete profile {user_id}")
        self._server.delete(user_id)

    def get_all_profiles(self, match=None):
        """ get all profiles
        Args:
            match: pattern to retreive the profiles (not regex)
        Return:
            dict with user_id -> vector
        """
        _LOGGER.info("get all profiles")
        my_dict = dict()
        for key in self._server.scan_iter(match=match):
            my_dict[key.decode("utf-8")] = json.loads(self._server.get(key))
        return my_dict

    def get_profile(self, user_id):
        """ get a specific profile
        Args:
            user_id: user_id of the profile
        Return:
            a vector (list of float)
        """
        _LOGGER.info(f"get profile {user_id}")
        res = self._server.get(user_id)
        if res is None:
            return res
        return json.loads(res)

    def set_profile(self, user_id, vector):
        """ create or modify a profile
        Args:
            user_id: user_id of the profile
            vector: list of float for that profile
        """
        _LOGGER.info(f"set profile {user_id} with {vector}")
        value = json.dumps(vector)
        self._server.set(user_id, value)

    def set_profiles(self, user_ids, vectors):
        """ create or modify multiple profiles at once

        The function use the pipeline object for better performance

        Args:
            user_ids: list of user_id
            vectors: list of vector
        """
        _LOGGER.info("set profiles in batch")
        pipeline = self._server.pipeline()
        for user_id, vector in zip(user_ids, vectors):
            value = json.dumps(vector)
            pipeline.set(user_id, value)
        pipeline.execute()
