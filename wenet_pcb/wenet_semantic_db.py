""" module that handle db to access to semantic routine
"""

from sqlalchemy import create_engine, Column, Integer, String, Time, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, joinedload
from wenet_pcb.wenet_logger import create_logger

_LOGGER = create_logger(__name__)
_Base = declarative_base()


class LabelsLocation(_Base):
    __tablename__ = "labels_locations"
    id = Column(Integer, primary_key=True)
    lat = Column(Float)
    lng = Column(Float)
    label_id = Column(Integer, ForeignKey("labels.id"))

    def to_dict(self):
        my_dict = dict()
        my_dict["id"] = self.id
        my_dict["lat"] = self.lat
        my_dict["lng"] = self.lng
        my_dict["label_id"] = self.label_id
        return my_dict


class Labels(_Base):
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def to_dict(self):
        my_dict = dict()
        my_dict["id"] = self.id
        my_dict["name"] = self.name
        return my_dict


class LabelsScore(_Base):
    __tablename__ = "labels_score"

    id = Column(Integer, primary_key=True)
    semantic_routine_id = Column(Integer, ForeignKey("semantic_routines.id"))
    label_location_id = Column(Integer, ForeignKey("labels_locations.id"))
    score = Column(Float)

    def to_dict(self):
        my_dict = dict()
        my_dict["id"] = self.id
        my_dict["semantic_routine_id"] = self.semantic_routine_id
        my_dict["label_location_id"] = self.label_location_id
        my_dict["score"] = self.score
        return my_dict


class SemanticRoutine(_Base):
    __tablename__ = "semantic_routines"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    weekday = Column(Integer)
    time_slot = Column(String)
    label_scores = relationship(LabelsScore)

    def to_dict(self):
        my_dict = dict()
        my_dict["id"] = self.id
        my_dict["user_id"] = self.user_id
        my_dict["weekday"] = self.weekday
        my_dict["time_slot"] = self.time_slot
        my_dict["labels_scores"] = [row.to_dict() for row in self.label_scores]
        return my_dict


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

    @classmethod
    def get_instance(cls, is_mock=False):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls(is_mock)
        return cls._INSTANCE


if __name__ == "__main__":
    semantic_routine_db = SemanticRoutineDB.get_instance(is_mock=True)
    semantic_routine_db.set_labels({1: "HOME", 2: "WORK"})
    for row in semantic_routine_db.get_labels():
        print(f"{row['id']} -> {row['name']}")

    semantic_routine_db.add_label_location(30, 30, 1)
    semantic_routine_db.add_label_location(40, 40, 2)
    semantic_routine_db.add_semantic_routine("toto", 1, "11:00", {1: 0.3, 2: 0.7})
    for row in semantic_routine_db.get_semantic_routines():
        print(f"res : {row}")
