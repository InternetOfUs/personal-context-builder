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
from wenet_profiles_writer import MockWenetSourceLabels, MockWenetSourceLocations


def train():
    source_locations = MockWenetSourceLocations()
    source_labels = MockWenetSourceLabels(source_locations)
    bow_trainer = BaseBOWTrainer(source_locations, source_labels)
    lda_model_untrained = SimpleLDA()
    model_trainer = BaseModelTrainer(
        source_locations, source_labels, bow_trainer, lda_model_untrained
    )
    lda_model = model_trainer.train()
    lda_model.save(filename="last_lda.p")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wenet Command line interface")
    parser.add_argument(
        "--train", help="train the model from the latest data", action="store_true"
    )
    parser.add_argument(
        "--update", help="update the profiles in the db", action="store_true"
    )
    parser.add_argument("--app_run", help="run the application", action="store_true")
    parser.add_argument(
        "--mock",
        help="use mock data/db instead of real wenet data",
        action="store_true",
    )
    args = parser.parse_args()
    if args.train:
        train()
    if args.update:
        pass  # TODO update profiles
    if args.app_run:
        pass  # TODO run the services
