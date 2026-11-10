import logging
from datetime import datetime

from extract import extract_air_quality
from transform import transform_air_quality
from load import load_data


# Create logs directory
import os
os.makedirs("logs", exist_ok=True)


# Configure logging
logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def run_pipeline():

    print("=" * 50)
    print("AIR QUALITY DATA ENGINEERING PIPELINE")
    print("=" * 50)

    logger.info("Pipeline execution started")

    start_time = datetime.now()

    try:

        # STEP 1: EXTRACTION
        print("\nSTEP 1: Extracting data...")
        logger.info("Starting data extraction")

        raw_data = extract_air_quality()

        raw_data.to_csv(
            "data/air_quality_raw.csv",
            index=False
        )

        logger.info(
            "Data extraction completed. Records: %d",
            len(raw_data)
        )

        print("Extracted records:", len(raw_data))


        # STEP 2: TRANSFORMATION
        print("\nSTEP 2: Transforming data...")
        logger.info("Starting data transformation")

        clean_data = transform_air_quality()

        logger.info(
            "Data transformation completed. Clean records: %d",
            len(clean_data)
        )

        print("Clean records:", len(clean_data))


        # STEP 3: LOADING
        print("\nSTEP 3: Loading into PostgreSQL...")
        logger.info("Starting database loading")

        load_data()

        logger.info("Database loading completed successfully")


        end_time = datetime.now()

        duration = (end_time - start_time).total_seconds()

        logger.info(
            "Pipeline completed successfully. Duration: %.2f seconds",
            duration
        )

        print("\n" + "=" * 50)
        print("PIPELINE EXECUTION SUCCESSFUL!")
        print("=" * 50)

        print("Execution time:", round(duration, 2), "seconds")


    except Exception:

        logger.exception("Pipeline execution failed")

        print("\nPIPELINE FAILED!")
        print("Check logs/pipeline.log for details")

        raise


if __name__ == "__main__":

    run_pipeline()