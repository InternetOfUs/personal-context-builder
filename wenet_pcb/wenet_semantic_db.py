""" module that handle db to access to semantic routine
"""

from sqlalchemy import create_engine, Column, Integer, String, Time, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, joinedload
from wenet_pcb.wenet_logger import create_logger
from copy import deepcopy

_LOGGER = create_logger(__name__)
_Base = declarative_base()


class DictViewable(object):
    def to_dict(self):
        my_dict = dict()
        for k, v in self.__dict__.items():
            if k is None or k[0] == "_":
                continue
            # Doesn't seem to work because __dict__ doesn't store 1-1 relationship
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

    def set_label(self, id, name, semantic_identifier):
        _LOGGER.debug(f"set label {id} -> {name}")
        label = Labels(id=id, name=name, semantic_identifier=semantic_identifier)
        self._session.add(label)

    def set_labels(self, labels_records):
        for label_record in labels_records:
            self.set_label(**label_record)

    def add_label_location(self, lat, lng, label_id):
        location_label = LabelsLocation(lat=lat, lng=lng, label_id=label_id)
        self._session.add(location_label)

    def get_labels(self):
        return [row.to_dict() for row in self._session.query(Labels).all()]

    def add_semantic_routine(self, user_id, weekday, time_slot, labels_scores_dict):
        semantic_routine = SemanticRoutine(
            user_id=user_id, weekday=weekday, time_slot=time_slot
        )
        for label_location_id, score in labels_scores_dict.items():
            label_score = LabelsScore(label_location_id=label_location_id, score=score)
            semantic_routine.label_scores.append(label_score)
            self._session.add(label_score)
        self._session.add(semantic_routine)
        self._session.commit()

    def get_semantic_routines(self, filter_exp=None):
        if filter_exp is not None:
            res = (
                self._session.query(SemanticRoutine)
                .options(joinedload("label_scores"))
                .filter(filter_exp())
                .all()
            )
        else:
            res = (
                self._session.query(SemanticRoutine)
                .options(joinedload("label_scores"))
                .all()
            )
        return [row.to_dict() for row in res]

    def get_semantic_routines_for_user(self, user_id):
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
