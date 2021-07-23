""" module that handle real-time

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,

"""
from __future__ import annotations
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict
import redis  # type: ignore
from regions_builder.models import UserLocationPoint, UserPlace  # type: ignore

from personal_context_builder import config
from personal_context_builder.wenet_logger import create_logger

_LOGGER = create_logger(__name__)


class DatabaseRealtimeLocationsHandlerBase(ABC):
    """Base interface for handling database access for the Realtime locations of the user

    is a dict of Singleton
    """

    _INSTANCES: Dict[int, DatabaseRealtimeLocationsHandlerBase] = dict()

    def __init__(self, db_index: int = 0):
        pass

    @classmethod
    def get_instance(cls, *args, db_index: int = 0, **kwargs):
        """get the instance or create if doesn't exist

        Can be have multiple instance when multiple db_index are used
        """
        if db_index not in cls._INSTANCES:
            cls._INSTANCES[db_index] = cls(*args, **kwargs)
        return cls._INSTANCES[db_index]

    @abstractmethod
    def update(self, userplaces: List[UserPlace]):
        """Update the userplaces"""

    @abstractmethod
    def get_all_users(self):
        """get all users"""

    @abstractmethod
    def get_users(self, users_id: str):
        """get some users"""


class DatabaseRealtimeLocationsHandlerMock(DatabaseRealtimeLocationsHandlerBase):
    def __init__(self, db_index: int = 0):
        self._my_dict: Dict[str, UserPlace] = dict()

    def update(self, userplaces: List[UserPlace]):
        _LOGGER.info("mock update real-time user locations")
        for userplace in userplaces:
            self._my_dict[userplace._user] = userplace

    def get_all_users(self):
        _LOGGER.info("mock get all real-time location of users")
        return self._my_dict

    def get_users(self, users_id: str):
        _LOGGER.info("mock get real-time location of some users")
        new_dict = dict()
        for user_id in users_id:
            new_dict[user_id] = self._my_dict[user_id]
        return new_dict


class DatabaseRealtimeLocationsHandler(DatabaseRealtimeLocationsHandlerBase):
    """Handle database to the redis server for real-time data

    Not thread safe

    """

    def __init__(
        self,
        db_index: int = 0,
        host: str = config.PCB_REALTIME_REDIS_HOST,
        port: int = config.PCB_REALTIME_REDIS_PORT,
    ):
        self._server = redis.Redis(host=host, port=port, db=db_index)
        try:
            self._server.ping()
        except:  # TODO catch specific exception
            raise Exception("Unable to access the Redis DB")

    def update(self, userplaces: List[UserPlace]):
        """update the db with userplaces"""
        _LOGGER.info("update real-time user locations")
        pipeline = self._server.pipeline()
        for userplace in userplaces:
            userplace._pts_t = userplace._pts_t.strftime(config.PCB_DATETIME_FORMAT)
            value = json.dumps(userplace.__dict__)
            pipeline.set(userplace._user, value)
        pipeline.execute()

    def get_all_users(self):
        """get all users locations

        Return:
            dict with user_id -> UserLocationPoint
        """
        _LOGGER.info("get all real-time users locations")
        my_dict = dict()
        for key in self._server.scan_iter():
            dict_user_location = json.loads(self._server.get(key))
            dict_user_location["_pts_t"] = datetime.strptime(
                dict_user_location["_pts_t"], config.PCB_DATETIME_FORMAT
            )
            my_dict[key.decode("utf-8")] = UserLocationPoint.from_dict(
                dict_user_location
            )
        return my_dict

    def get_users(self, users_id: str):
        """get some users locations
        Args:
            users_id -> list of user_id

        Return:
            dict with user_id -> UserLocationPoint
        """
        _LOGGER.info("mock get real-time location of some users")
        new_dict = dict()
        for user_id in users_id:
            user_location_dict = json.loads(self._server.get(user_id))
            new_dict[user_id] = UserLocationPoint.from_dict(user_location_dict)
        return new_dict
