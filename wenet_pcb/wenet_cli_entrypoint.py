"""
CLI entrypoint for wenet
  - app_run
  - train
  - update
  - mock
"""

import argparse
from uuid import uuid4
from wenet_pcb.wenet_trainer import BaseBOWTrainer, BaseModelTrainer
from wenet_pcb import wenet_analysis_models, wenet_pipelines
from wenet_pcb.wenet_analysis_models import SimpleLDA, SimpleBOW
from wenet_pcb.wenet_data_loading import (
    MockWenetSourceLabels,
    MockWenetSourceLocations,
    closest_users,
    compare_routines,
)
from wenet_pcb.wenet_profiles_writer import ProfileWritterFromMock, ProfileWritter
from wenet_pcb.wenet_user_profile_db import (
    DatabaseProfileHandlerMock,
    DatabaseProfileHandler,
)
from wenet_pcb.wenet_realtime_user_db import (
    DatabaseRealtimeLocationsHandler,
    DatabaseRealtimeLocationsHandlerMock,
)
from wenet_pcb.sanic_app import WenetApp
from wenet_pcb import config
from wenet_pcb.wenet_logger import create_logger

from scipy import spatial

_LOGGER = create_logger(__name__)


def force_update_locations(is_mock=False):
    if is_mock:
        db = DatabaseRealtimeLocationsHandlerMock.get_instance()
        newest_locations = [
            MockWenetSourceLocations._create_fake_locations(str(uuid4()), nb=1)[0]
            for _ in range(100)
        ]

    else:
        db = DatabaseRealtimeLocationsHandler.get_instance()

        # TODO changeme
        newest_locations = [
            MockWenetSourceLocations._create_fake_locations(str(uuid4()), nb=1)[0]
            for _ in range(100)
        ]
    db.update(newest_locations)


def closest(lat, lng, N, is_mock=False):
    sorted_users_locations = closest_users(lat, lng, N, is_mock)
    for distance, user_location in sorted_users_locations:
        print(f"{distance:10d}m {user_location._user}")


def train(is_mock=False):
    for (
        pipeline_class_name,
        map_model_to_db,
    ) in config.MAP_PIPELINE_TO_MAP_MODEL_TO_DB.items():
        pipeline_class = getattr(wenet_pipelines, pipeline_class_name)
        pipeline = pipeline_class(
            mock_db=is_mock, mock_datasources=is_mock, db_map=map_model_to_db
        )
        _LOGGER.info(f"train -- pipeline {pipeline_class_name}")
        pipeline.train()


def update(is_mock=False):
    for (
        pipeline_class_name,
        map_model_to_db,
    ) in config.MAP_PIPELINE_TO_MAP_MODEL_TO_DB.items():
        pipeline_class = getattr(wenet_pipelines, pipeline_class_name)
        pipeline = pipeline_class(
            mock_db=is_mock, mock_datasources=is_mock, db_map=map_model_to_db
        )
        _LOGGER.info(f"update -- pipeline {pipeline_class_name}")
        pipeline.update()


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
    models = [model_name.split(":")[0] for model_name in config.MAP_MODEL_TO_DB.keys()]
    for model_name in models:
        model_doc = getattr(wenet_analysis_models, model_name).__doc__
        print(f"[{model_name}] \t{model_doc}")


def compare_routines_cmd(
    source_user, users, model, function=spatial.distance.cosine, is_mock=False
):
    res = compare_routines(source_user, users, model, function, is_mock=is_mock)
    print(res)


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
    parser.add_argument(
        "--closest",
        help="get N closest users from lat, lng",
        nargs=3,
        metavar=("lat", "lng", "N"),
    )
    parser.add_argument(
        "--force_update_locations",
        help="update the locations of the users",
        action="store_true",
    )
    parser.add_argument(
        "--compare_routines", help="compare users (should be seaparated by ':')"
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
    if args.force_update_locations:
        force_update_locations(args.mock)
    if args.closest:
        lat = float(args.closest[0])
        lng = float(args.closest[1])
        N = int(args.closest[2])
        closest(lat, lng, N, args.mock)
    if args.compare_routines:
        source, *users = args.compare_routines.split(":")
        compare_routines_cmd(source, users, "SimpleLDA:PipelineBOW", is_mock=args.mock)
    if args.app_run:
        run_app()
