"""
module that work with Y@N data
"""
import argparse


def write_to_json(json_output_file, gps_file, ambiance_file=None, trung_file=None):
    """ convert the data to a json file with StayPoints, StayRegion and LocationPoint.
    (WIP) - TODO write this function
    Args:
        json_output_file: file that will contain the data transformed
        gps_file: file that contain the gps records
        ambiance_file: file that contain ambiance file (from survey)
        trung_file: json file given by Trung that contain custom labels
    """
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="convert the data to a json file with StayPoints, StayRegion and LocationPoint."
    )
    parser.add_argument(
        "json_output_file", type=str, help="file that will contain the data transformed"
    )
    parser.add_argument("gps_file", type=str, help="file that contain the gps records")
    parser.add_argument(
        "--ambiance_file",
        type=str,
        help="file that contain ambiance file (from survey)",
    )
    parser.add_argument(
        "--trung_file",
        type=str,
        help="json file given by Trung that contain custom labels",
    )
    args = parser.parse_args()
    write_to_json(
        args.json_output_file, args.gps_file, args.ambiance_file, args.trung_file
    )
