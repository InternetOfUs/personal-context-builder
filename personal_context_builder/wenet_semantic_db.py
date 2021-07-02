""" module that handle db to access to semantic routine

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,

"""

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Time,
    ForeignKey,
    Float,
    event,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, joinedload
from personal_context_builder.wenet_logger import create_logger
from personal_context_builder.wenet_postgres import PostresqlCoordinator
from personal_context_builder import config
from copy import deepcopy

_LOGGER = create_logger(__name__)
_Base = declarative_base()


@event.listens_for(_Base.metadata, "after_create")
def receive_after_create(target, connection, tables, **kw):
    "listen for the 'after_create' event"
    if tables:
        _LOGGER.warn(f"some postgresql has been created {tables}")


class DictViewable(object):
    def to_dict(self):
        my_dict = dict()
        for k, v in self.__dict__.items():
            if k is None or k[0] == "_":
                continue
            # Doesn't seem to work because __dict__ doesn't store 1-1 relationship
            # TODO use inspect for sqlachemy to solve that
            if isinstance(v, (DictViewable,)):
                my_dict[k] = v.to_dict()
            elif isinstance(v, list):
                my_dict[k] = self._to_dict_rec(v)
            else:
                my_dict[k] = deepcopy(v)
        return my_dict

    @classmethod
    def _to_dict_rec(cls, iterable):
        res = []
        for item in iterable:
            if isinstance(item, list):
                elem = cls._to_dict_rec(item)
            elif isinstance(item, (DictViewable,)):
                elem = item.to_dict()
            else:
                elem = deepcopy(item)
            res.append(elem)
        return res


class LabelsLocation(_Base, DictViewable):
    __tablename__ = "labels_locations"
    id = Column(Integer, primary_key=True)
    lat = Column(Float)
    lng = Column(Float)
    label_id = Column(Integer, ForeignKey("labels.id"))
    label = relationship("Labels", uselist=False, backref="label_location")

    def to_dict(self):
        my_dict = super().to_dict()
        my_dict["label"] = self.label.to_dict()
        return my_dict


class Labels(_Base, DictViewable):
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    semantic_identifier = Column(Integer)


class LabelsScore(_Base, DictViewable):
    __tablename__ = "labels_score"

    id = Column(Integer, primary_key=True)
    semantic_routine_id = Column(Integer, ForeignKey("semantic_routines.id"))
    label_location_id = Column(Integer, ForeignKey("labels_locations.id"))
    label_location = relationship(
        "LabelsLocation", uselist=False, backref="label_scores"
    )
    score = Column(Float)

    def to_dict(self):
        my_dict = super().to_dict()
        my_dict["label_location"] = self.label_location.to_dict()
        return my_dict


class SemanticRoutine(_Base, DictViewable):
    __tablename__ = "semantic_routines"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    weekday = Column(Integer)
    time_slot = Column(String)
    label_scores = relationship(LabelsScore)


class SemanticRoutineDB(object):
    """class that handle semantic routines CRUD access."""

    _INSTANCE = None

    def __init__(self, is_mock=False):
        self._is_mock = True
        self._db_name = config.DEFAULT_SEMANTIC_DB_NAME
        self._engine = PostresqlCoordinator.get_engine(self._db_name, self._is_mock)
        self.create_if_not_exist()

    def create_if_not_exist(self):
        """create the table if they don't exist yet"""
        _Base.metadata.create_all(self._engine, checkfirst=True)

    def set_label(self, id, name, semantic_identifier):
        """create/update a label"""
        _LOGGER.debug(f"set label {id} -> {name}")
        label = Labels(id=id, name=name, semantic_identifier=semantic_identifier)
        with PostresqlCoordinator.get_new_managed_session(
            self._db_name, self._is_mock
        ) as session:
            session.add(label)

    def set_labels(self, labels_records):
        """create/update list of labels

        Current implementation does 1 session per label
        """
        for label_record in labels_records:
            self.set_label(**label_record)

    def add_label_location(self, lat, lng, label_id):
        """create a new label location"""
        location_label = LabelsLocation(lat=lat, lng=lng, label_id=label_id)
        with PostresqlCoordinator.get_new_managed_session(
            self._db_name, self._is_mock
        ) as session:
            session.add(location_label)

    def get_labels(self):
        """get all existing labels"""
        with PostresqlCoordinator.get_new_managed_session(
            self._db_name, self._is_mock
        ) as session:
            session = PostresqlCoordinator.get_new_session(self._db_name, self._is_mock)
            return [row.to_dict() for row in session.query(Labels).all()]

    def add_semantic_routine(self, user_id, weekday, time_slot, labels_scores_dict):
        """create new routine for a time_slot"""
        semantic_routine = SemanticRoutine(
            user_id=user_id, weekday=weekday, time_slot=time_slot
        )
        with PostresqlCoordinator.get_new_managed_session(
            self._db_name, self._is_mock
        ) as session:
            for label_location_id, score in labels_scores_dict.items():
                label_score = LabelsScore(
                    label_location_id=label_location_id, score=score
                )
                semantic_routine.label_scores.append(label_score)
                session.add(label_score)
            session.add(semantic_routine)

    def get_semantic_routines(self, filter_exp=None):
        """get the list of routines given filter expression (all if None)"""
        with PostresqlCoordinator.get_new_managed_session(
            self._db_name, self._is_mock
        ) as session:
            if filter_exp is not None:
                res = (
                    session.query(SemanticRoutine)
                    .options(joinedload("label_scores"))
                    .filter(filter_exp())
                    .all()
                )
            else:
                res = (
                    session.query(SemanticRoutine)
                    .options(joinedload("label_scores"))
                    .all()
                )
            return [row.to_dict() for row in res]

    def get_semantic_routines_for_user(self, user_id):
        """get the semantic routines for a given user"""
        return self.get_semantic_routines(
            filter_exp=lambda user_id=user_id: SemanticRoutine.user_id == user_id
        )

    @classmethod
    def get_instance(cls, is_mock=False):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls(is_mock)
        return cls._INSTANCE


if __name__ == "__main__":
    from pprint import pprint

    semantic_routine_db = SemanticRoutineDB.get_instance(is_mock=True)
    semantic_routine_db.set_labels(
        [
            {"id": 1, "name": "HOME", "semantic_identifier": 1},
            {"id": 2, "name": "WORK", "semantic_identifier": 2},
        ]
    )
    print("List of labels")
    for row in semantic_routine_db.get_labels():
        pprint(row)

    semantic_routine_db.add_label_location(30, 30, 1)
    semantic_routine_db.add_label_location(40, 40, 2)
    semantic_routine_db.add_semantic_routine("toto", 1, "11:00", {1: 0.3, 2: 0.7})
    print("List of routine for user toto")
    for row in semantic_routine_db.get_semantic_routines_for_user("toto"):
        pprint(row)
