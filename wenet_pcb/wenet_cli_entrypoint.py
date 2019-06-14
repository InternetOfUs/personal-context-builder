"""
CLI entrypoint for wenet
  - app_run
  - train
  - update
  - mock
"""

import argparse
from wenet_pcb.wenet_trainer import BaseBOWTrainer, BaseModelTrainer
from wenet_pcb import wenet_analysis_models
from wenet_pcb.wenet_analysis_models import SimpleLDA, SimpleBOW
from wenet_pcb.wenet_data_loading import MockWenetSourceLabels, MockWenetSourceLocations
from wenet_pcb.wenet_profiles_writer import ProfileWritterFromMock, ProfileWritter
from wenet_pcb.wenet_user_profile_db import (
    DatabaseProfileHandlerMock,
    DatabaseProfileHandler,
)
from wenet_pcb.sanic_app import WenetApp
from wenet_pcb import config
from wenet_pcb.wenet_logger import create_logger

_LOGGER = create_logger(__name__)


def train(is_mock=False):
    if is_mock:
        _LOGGER.info("Training on mock data")
        source_locations = MockWenetSourceLocations()
        source_labels = MockWenetSourceLabels(source_locations)
        bow_trainer = BaseBOWTrainer(source_locations, source_labels)
        for model_class_name, db_index in config.MAP_MODEL_TO_DB.items():
            _LOGGER.info(f"Train model {model_class_name}")
            model_class = getattr(wenet_analysis_models, model_class_name)
            model_untrained = model_class()
            model_trainer = BaseModelTrainer(
                source_locations, source_labels, bow_trainer, model_untrained
            )
            model = model_trainer.train()
            model.save(filename=f"_models_{db_index:02d}_{model_class_name}.p")
            _LOGGER.info(f"Model {model_class_name} saved")
        #  model_untrained = SimpleLDA()
        _LOGGER.info("done")


def update(is_mock=False):
    if is_mock:
        _LOGGER.info(f"updating profiles on mock data")
        source_locations = MockWenetSourceLocations()
        source_labels = MockWenetSourceLabels(source_locations)
        bow_trainer = BaseBOWTrainer(source_locations, source_labels)
        for model_class_name, db_index in config.MAP_MODEL_TO_DB.items():
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
                DatabaseProfileHandlerMock.get_instance(db_index=db_index),
            )
            profile_writter.update_profiles()
            _LOGGER.info("profiles updated")
        _LOGGER.info("done")
    else:  # pragma: no cover
        _LOGGER.info(f"updating profiles on real data (mock for now, TODO changeme)")
        source_locations = MockWenetSourceLocations()
        source_labels = MockWenetSourceLabels(source_locations)
        bow_trainer = BaseBOWTrainer(source_locations, source_labels)
        for model_class_name, db_index in config.MAP_MODEL_TO_DB.items():
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
                DatabaseProfileHandler.get_instance(db_index=db_index),
            )
            profile_writter.update_profiles()
            _LOGGER.info("profiles updated")
        _LOGGER.info("done")


def show_profile(user_id, is_mock=False):
    for db_index in config.MAP_DB_TO_MODEL.keys():
        if is_mock:
            profile = DatabaseProfileHandlerMock.get_instance(
                db_index=db_index
            ).get_profile(user_id)
        else:  # pragma: no cover
            profile = DatabaseProfileHandler.get_instance(
                db_index=db_index
            ).get_profile(user_id)
        print(f"DB_INDEX : {db_index:02d} - [{user_id}] {profile}")


def show_all_profiles(is_mock=False):
    for db_index in config.MAP_DB_TO_MODEL.keys():
        if is_mock:
            users_profiles = DatabaseProfileHandlerMock.get_instance(
                db_index=db_index
            ).get_all_profiles()
        else:  # pragma: no cover
            users_profiles = DatabaseProfileHandler.get_instance(
                db_index=db_index
            ).get_all_profiles()
        print(f"number of profiles for DB_INDEX {db_index:02d}: {len(users_profiles)}")
        for user_id, profile in users_profiles.items():
            print(f"\t[{user_id}] {profile}")


def clean_db_cmd(is_mock=False):
    for db_index in config.MAP_DB_TO_MODEL.keys():
        if is_mock:
            DatabaseProfileHandlerMock.get_instance(db_index=db_index).clean_db()
        else:  # pragma: no cover
            DatabaseProfileHandler.get_instance(db_index=db_index).clean_db()


def show_models():
    res = dict()
    for model_name in config.MAP_MODEL_TO_DB.keys():
        model_doc = getattr(wenet_analysis_models, model_name).__doc__
        print(f"[{model_name}] \t{model_doc}")


def run_app():
    wenet_app = WenetApp()
    wenet_app.run()


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(description="Wenet Command line interface")
    parser.add_argument(
        "--train", help="train the model from the latest data", action="store_true"
    )
    parser.add_argument(
        "--update", help="update the profiles in the db", action="store_true"
    )
    parser.add_argument("--clean_db", help="clean the db", action="store_true")
    parser.add_argument("--show", help="show a specific profile from the db")
    parser.add_argument(
        "--show_all", help="show all profiles from the db", action="store_true"
    )
    parser.add_argument("--app_run", help="run the application", action="store_true")
    parser.add_argument(
        "--show_models", help="show the list of models", action="store_true"
    )
    parser.add_argument(
        "--mock",
        help="use mock data/db instead of real wenet data",
        action="store_true",
    )
    args = parser.parse_args()
    if args.clean_db:
        clean_db_cmd(args.mock)
    if args.train:
        train(args.mock)
    if args.update:
        update(args.mock)
    if args.show_all:
        show_all_profiles(args.mock)
    if args.show:
        show_profile(args.show, args.mock)
    if args.show_models:
        show_models()
    if args.app_run:
        run_app()
