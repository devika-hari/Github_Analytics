from extract import run_extract
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

        # ---- Placeholder for next steps ----
        # transformed_data = run_transform(repos)
        # success = run_load(transformed_data)

    except Exception as e:
        # Catch any unexpected runtime error
        print("Extraction failed due to unexpected error. Check extract.log for details.\n")
        logging.exception("Unexpected error in main during extraction")

if __name__ == "__main__":
    main()
