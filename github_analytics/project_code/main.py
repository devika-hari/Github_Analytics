from github_analytics.project_code.extract import run_extract
from github_analytics.project_code.staging import run_staging
from config import *

import logging

logging.basicConfig(
    filename="../git_analytics.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("git_analytics")
logger.info("Main ETL started.")

def main():
    #extract
    try:
        repos = run_extract(no_of_days,min_stars,max_pages,sort,order,per_page)
        if not repos:
            print("Extraction failed. Please check log for details.Exiting...\n")
            logger.error("Extraction returned empty or failed.")
            return
        print("Extraction completed successfully. Proceeding to Staging...\n")
        logger.info("Extraction completed successfully.")
    except Exception as e:
        print("Extraction failed due to unexpected error. Check log for details.Exiting...\n")
        logger.error(f"Unexpected error in main during extraction: {e}")
        return
    #staging
    try:
        stg_success=run_staging(repos)
        if stg_success== True:
            print("Data loaded to database.")
            logger.info("Data load into staging successful.")
        else:
            print("Data Loading encountered errors..Exiting...")
            logger.error("Data Loading encountered errors.")
            return

    except Exception as e:
        print("Database Load failed due to unexpected error. Check log for details.\n")
        logger.error(f"Unexpected error in main during staging: {e} ")
        return

    print("ETL Completed successfully.")
    logger.info("ETL Completed successfully.")
    print("To view the dashboard, please run manually:")
    print("    streamlit run dashboard.py")

if __name__ == "__main__":
    main()
