"""
CLI entrypoint for wenet
  - app_run
  - train
  - update
  - mock
"""

import argparse
from wenet_trainer import BaseBOWTrainer, BaseModelTrainer
from wenet_analysis_models import SimpleLDA
from wenet_data_loading import MockWenetSourceLabels, MockWenetSourceLocations
from wenet_profiles_writer import ProfileWritterFromMock, ProfileWritter
from wenet_user_profile_db import get_all_profiles, get_profile, clean_db


def train(is_mock=False):
    if is_mock:
        print(f"Training on mock data")
        source_locations = MockWenetSourceLocations()
        source_labels = MockWenetSourceLabels(source_locations)
        bow_trainer = BaseBOWTrainer(source_locations, source_labels)
        lda_model_untrained = SimpleLDA()
        model_trainer = BaseModelTrainer(
            source_locations, source_labels, bow_trainer, lda_model_untrained
        )
        lda_model = model_trainer.train()
        lda_model.save(filename="last_lda.p")
        print(f"done")


def update(is_mock=False):
    if is_mock:
        print(f"updating profiles on mock data")
        source_locations = MockWenetSourceLocations()
        source_labels = MockWenetSourceLabels(source_locations)
        bow_trainer = BaseBOWTrainer(source_locations, source_labels)
        model = SimpleLDA.load("last_lda.p")
        profile_writter = ProfileWritterFromMock(
            source_locations, source_labels, model, bow_trainer
        )
        profile_writter.update_profiles()
        print(f"done")
    else:
        print(f"updating profiles on real data (mock for now, TODO changeme)")
        source_locations = MockWenetSourceLocations()
        source_labels = MockWenetSourceLabels(source_locations)
        bow_trainer = BaseBOWTrainer(source_locations, source_labels)
        model = SimpleLDA.load("last_lda.p")
        profile_writter = ProfileWritter(
            source_locations, source_labels, model, bow_trainer
        )
        profile_writter.update_profiles()
        print(f"done")


def show_profile(user_id):
    profile = get_profile(user_id)
    print(f"[{user_id}] {profile}")


def show_all_profiles():
    users_profiles = get_all_profiles()
    print(f"number of profiles : {len(users_profiles)}")
    for user_id, profile in users_profiles.items():
        print(f"[{user_id}] {profile}")


def clean_db_cmd():
    clean_db()


if __name__ == "__main__":
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
        "--mock",
        help="use mock data/db instead of real wenet data",
        action="store_true",
    )
    args = parser.parse_args()
    if args.clean_db:
        clean_db_cmd()
    if args.train:
        train(args.mock)
    if args.update:
        update(args.mock)
    if args.show_all:
        show_all_profiles()
    if args.app_run:
        pass  # TODO run the services
