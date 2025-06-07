import logging
from datetime import datetime

import awswrangler as wr
import pandas as pd

from powerbi_etl.utils import S3_BUCKET_NAME, SELENIUM_HANDLER, parsed_args


class BaseVariables:
    arguments = parsed_args
    environment = arguments.environment
    prefix = arguments.etl_prefix


class DataExtractor:
    # Configure logging.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    base_variables = BaseVariables()
    selenium_handler = SELENIUM_HANDLER
    df = None

    def __init__(self) -> None:
        # Creates a logger.
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract(self) -> pd.DataFrame:
        """Extracts Data from the Source URL."""
        raise NotImplementedError("Extract Method Not Implemented.")

    def transform(self) -> pd.DataFrame:
        """Transforms Data to feed into S3."""
        raise NotImplementedError("Transform Method Not Implemented.")

    def load(self):
        """Load the Transformed Data into AWS S3."""
        self.logger.info("Initiating the Data Loading Method.")

        self.df["series_id"] = self.base_variables.prefix + "\\" + self.df["series_id"]
        file_name = f"{self.__class__.__name__.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        s3_path = f"s3://{S3_BUCKET_NAME}/{file_name}"
        wr.s3.to_csv(df=self.df, path=s3_path, index=False)

        self.logger.info("DataFrame Uploaded to S3 Successfully.")

    def etl(self):
        try:
            self.extract()
        except Exception as err:
            raise RuntimeError(
                f"Scraper failed at Extraction. Error was {err}"
            ) from err
        try:
            self.transform()
        except Exception as err:
            raise RuntimeError(
                f"Scraper failed at Transformation. Error was {err}"
            ) from err
        try:
            self.load()
        except Exception as err:
            raise RuntimeError(f"Scraper failed at Upload. Error was {err}") from err
