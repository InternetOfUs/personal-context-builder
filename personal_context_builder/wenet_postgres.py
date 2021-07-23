"""
module that handle db connections to the sql databases

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,

"""
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from personal_context_builder.wenet_logger import create_logger

_LOGGER = create_logger(__name__)


class PostresqlCoordinator(object):

    _INSTANCES = dict()

    def __init__(self, db_name: str, is_mock: bool = False):
        self._is_mock = True
        if is_mock:
            #  In-memory db
            self._engine = create_engine("sqlite://")
            _LOGGER.info("mocked semantic database with in-memory db")
        else:
            #  TODO put postresql db with good strategy for credential
            _LOGGER.warn(
                "True semantic database not implemented yet, using in-memory db"
            )
            self._engine = create_engine("sqlite://")
        self._Session = sessionmaker(bind=self._engine)

    @classmethod
    @contextmanager
    def get_new_managed_session(cls, db_name: str, is_mock: bool = False):
        session = cls.get_new_session(db_name, is_mock)
        try:
            yield session
            session.commit()
        except Exception as e:
            _LOGGER.error(f"error when commiting postgresql instructions {e}")
            _LOGGER.warn("Unable to commit postgresql instructions, rollback")
            session.rollback()
        finally:
            session.close()

    @classmethod
    def get_instance(cls, db_name: str, is_mock: bool = False):
        if db_name not in cls._INSTANCES or cls._INSTANCES[db_name] is None:
            cls._INSTANCES[db_name] = cls(db_name, is_mock)
        return cls._INSTANCES[db_name]

    @classmethod
    def get_engine(cls, db_name: str, is_mock: bool = False):
        instance = cls.get_instance(db_name, is_mock)
        return instance._engine

    @classmethod
    def get_new_session(cls, db_name: str, is_mock: bool = False):
        instance = cls.get_instance(db_name, is_mock)
        return instance._Session()
