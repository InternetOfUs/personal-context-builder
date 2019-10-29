""" module that handle db to access to semantic routine
"""

from sqlalchemy import create_engine, Column, Integer, String, Time, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from wenet_pcb.wenet_logger import create_logger

_LOGGER = create_logger(__name__)
_Base = declarative_base()


class Labels(_Base):
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class LabelsScore(_Base):
    __tablename__ = "labels_score"

    id = Column(Integer, primary_key=True)
    semantic_routine_id = Column(Integer, ForeignKey("semantic_routines.id"))
    label_id = Column(Integer, ForeignKey("labels.id"))
    score = Column(Float)


class SemanticRoutine(_Base):
    __tablename__ = "semantic_routines"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    weekday = Column(Integer)
    time_slot = Column(String)
    label_scores = relationship(LabelsScore)


class SemanticRoutineDB(object):

    _INSTANCE = None

    def __init__(self, is_mock=False):
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
        Session = sessionmaker(bind=self._engine)
        self._session = Session()
        self.create_if_not_exist()

    def create_if_not_exist(self):
        _Base.metadata.create_all(self._engine, checkfirst=True)

    def set_label(self, id, name):
        _LOGGER.debug(f"set label {id} -> {name}")
        label = Labels(id=id, name=name)
        self._session.add(label)

    def set_labels(self, labels_dict):
        for id, name in labels_dict.items():
            self.set_label(id, name)

    def get_labels(self):
        return self._session.query(Labels).all()

    @classmethod
    def get_instance(cls, is_mock=False):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls(is_mock)
        return cls._INSTANCE


if __name__ == "__main__":
    semantic_routine_db = SemanticRoutineDB.get_instance(is_mock=True)
    semantic_routine_db.set_labels({1: "HOME", 2: "WORK"})
    for row in semantic_routine_db.get_labels():
        print(f"{row.id} -> {row.name}")
