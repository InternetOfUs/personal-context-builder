"""
module that handle db connections to the sql databases
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from wenet_pcb.wenet_logger import create_logger

_LOGGER = create_logger(__name__)


class PostresqlCoordinator(object):

    _INSTANCES = dict()

    def __init__(self, db_name, is_mock=False):
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
    def get_instance(cls, db_name, is_mock=False):
        if db_name not in cls._INSTANCES or cls._INSTANCES[db_name] is None:
            cls._INSTANCES[db_name] = cls(db_name, is_mock)
        return cls._INSTANCES[db_name]

    @classmethod
    def get_engine(cls, db_name, is_mock=False):
        instance = cls.get_instance(db_name, is_mock)
        return instance._engine

    @classmethod
    def get_new_session(cls, db_name, is_mock=False):
        instance = cls.get_instance(db_name, is_mock)
        _LOGGER.info(f"Create new session to {db_name}")
        return instance._Session()
