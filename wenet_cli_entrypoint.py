"""
CLI entrypoint for wenet
  - app_run
  - train
  - update
  - mock
"""

import argparse

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
        pass  # TODO train
    if args.update:
        pass  # TODO update profiles
    if args.app_run:
        pass  # TODO run the services
