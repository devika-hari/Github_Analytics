from extract import run_extract
from staging import run_staging

import logging

# Optional: main-level logging for unexpected errors
logging.basicConfig(
    filename="main.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    print("Starting ETL process...\n")
    no_of_days=30 #pushed
    min_stars=200
    max_pages=10
    per_page=30
    sort="stars"
    order="desc"
    try:
        # ---- Extraction ----
        repos = run_extract(no_of_days,min_stars,max_pages,sort,order,per_page)  # extract.py handles detailed prints and logging
        if not repos:
            print("Extraction failed. Please check extract.log for details.\n")
            return
        print("✅ Extraction completed successfully. Proceeding to next step...\n")
    except Exception as e:
        # Catch any unexpected runtime error
        print("Extraction failed due to unexpected error. Check extract.log for details.\n")
        logging.exception("Unexpected error in main during extraction")
    try:
        stg_success=run_staging(repos)
        if stg_success== True:
            print("Data loaded to database.")
            logging.info("Data Load successful.")
        else:
            print("Data Loading encountered errors..Exiting...")
            return
    except Exception as e:
        print("Database Load failed due to unexpected error. Check staging.log for details.\n")
        logging.exception("Unexpected error in main during staging")

if __name__ == "__main__":
    main()
