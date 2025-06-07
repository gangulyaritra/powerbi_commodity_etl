import argparse
import os

from powerbi_etl.utils.selenium_tools import Selenium

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "powerbi-etl-scrape")


# Initiate all the handlers here.
SELENIUM_HANDLER = Selenium(headless=False, **{"window-size": "1920,1080"})


def parse_args() -> argparse.Namespace:
    """
    Argument parser

    Returns:
        Args: an argparse object.
    """

    parser = argparse.ArgumentParser(description="Parameters for ETL")

    # Add argument for environment.
    parser.add_argument(
        "--environment",
        help="Which environment to run the project in?",
        default="tests",
        choices=["tests", "prod"],
    )

    args, _ = parser.parse_known_args()

    args.etl_prefix = "powerbi" if args.environment == "prod" else "tests\\powerbi"

    return args


parsed_args = parse_args()
