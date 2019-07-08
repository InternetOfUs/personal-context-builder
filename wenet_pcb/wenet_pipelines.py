"""
module with all pipeline for training / updading models/DB
"""

from abc import ABC, abstractmethod
from wenet_pcb.wenet_logger import create_logger
from wenet_pcb.wenet_trainer import BaseBOWTrainer, BaseModelTrainer
from wenet_pcb import wenet_analysis_models
from wenet_pcb.wenet_data_loading import MockWenetSourceLabels, MockWenetSourceLocations
from wenet_pcb.wenet_profiles_writer import ProfileWritterFromMock, ProfileWritter
from wenet_pcb.wenet_user_profile_db import (
    DatabaseProfileHandlerMock,
    DatabaseProfileHandler,
)
from wenet_pcb import config

_LOGGER = create_logger(__name__)


class BasePipeline(ABC):
    def __init__(self, mock_db=False, mock_datasources=False, db_map=None):
        self._mock_db = mock_db
        self._mock_datasources = mock_datasources
        self._db_map = db_map
        if self._db_map is None:
            raise ValueError("db_map must not be None")

    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def update(self):
        pass


class PipelineBOW(BasePipeline):
    """
    Pipeline that uses BOW as features
    """

    def __init__(self, mock_db=False, mock_datasources=False, db_map=None):
        super().__init__(mock_db, mock_datasources, db_map)

    def train(self):
        if self._mock_datasources:
            _LOGGER.info("Training from mocked data sources")
            source_locations = MockWenetSourceLocations()
            source_labels = MockWenetSourceLabels(source_locations)
        else:
            _LOGGER.info("Training from real data sources")
            source_locations = MockWenetSourceLocations()
            source_labels = MockWenetSourceLabels(source_locations)
        bow_trainer = BaseBOWTrainer(source_locations, source_labels)
        for model_class_name, db_index in self._db_map.items():
            _LOGGER.info(f"Train model {model_class_name}")
            model_class = getattr(wenet_analysis_models, model_class_name)
            model_untrained = model_class()
            model_trainer = BaseModelTrainer(
                source_locations, source_labels, bow_trainer, model_untrained
            )
            model = model_trainer.train()
            model.save(filename=f"_models_{db_index:02d}_{model_class_name}.p")
            _LOGGER.info(f"Model {model_class_name} saved")
        _LOGGER.info("done")

    def update(self):
        if self._mock_datasources:
            _LOGGER.info(f"updating profiles from mocked data sources")
            source_locations = MockWenetSourceLocations()
            source_labels = MockWenetSourceLabels(source_locations)
        else:
            _LOGGER.info(f"updating profiles from real data sources")
            source_locations = MockWenetSourceLocations()
            source_labels = MockWenetSourceLabels(source_locations)
        bow_trainer = BaseBOWTrainer(source_locations, source_labels)
        if self._mock_db:
            _LOGGER.info("Mocked database will be used")
            profile_handler_class = DatabaseProfileHandlerMock
        else:
            _LOGGER.info("Real database will be used")
            profile_handler_class = DatabaseProfileHandler
        for model_class_name, db_index in self._db_map.items():
            _LOGGER.info(
                f"Update profiles at DB {db_index:02d} from model {model_class_name}"
            )
            model_class = getattr(wenet_analysis_models, model_class_name)
            model = model_class.load(f"_models_{db_index:02d}_{model_class_name}.p")
            profile_writter = ProfileWritter(
                source_locations,
                source_labels,
                model,
                bow_trainer,
                profile_handler_class.get_instance(db_index=db_index),
            )
            profile_writter.update_profiles()
            _LOGGER.info("profiles updated")
        _LOGGER.info("done")
