import sqlite3
import logging
import pandas as pd
from datetime import datetime, timedelta

logging.basicConfig(
    filename="staging.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__) #returns the same logger object if it already exists.

# Custom exception inherits from the built-in RuntimeError
class DatabaseInitializationError(RuntimeError):
    #Custom exception for database setup failures
    pass

class GitHubStaging:
    def __init__(self, db_path="github_repos.db"):
        self.db_path = db_path

        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self._create_tables()
        except sqlite3.Error as e:
            # 1. Log the low-level technical error for debugging
            logging.error(f"Failed to connect to DB: {e}")
            # 2. Raise a high-level exception, chaining the original error
            raise DatabaseInitializationError(
                "The database could not be initialized. Check logs for details."
            ) from e
        else:
            logging.info("Database connection successful.")


#Create SQLite tables for repos and contributors.
    def _create_tables(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS repositories (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    full_name TEXT,
                    html_url TEXT,
                    description TEXT,
                    stargazers_count INTEGER,
                    watchers_count INTEGER,
                    forks_count INTEGER,
                    open_issues_count INTEGER,
                    language TEXT,
                    topics TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    pushed_at TEXT
                )
                """)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Failed to create tables: {e}")
            print("Table creation failed. Check logs for details.")
        else:
            logging.info("Table creation successful.")

#Insert extracted JSON cleanly.
    def insert_repos(self, repos):
        try:
            for repo in repos:
                topics = ",".join(repo.get("topics", []))
                self.cursor.execute("""
                    INSERT OR REPLACE INTO repositories (
                        id, name, full_name, html_url, description,
                        stargazers_count, watchers_count, forks_count, open_issues_count,
                        language, topics, created_at, updated_at, pushed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    repo["id"], repo["name"], repo["full_name"], repo["html_url"],
                    repo.get("description"), repo["stargazers_count"], repo["watchers_count"],
                    repo["forks_count"], repo["open_issues_count"], repo.get("language"),
                    topics, repo["created_at"], repo["updated_at"], repo["pushed_at"]
                ))
                self.conn.commit()
        except Exception as e:
            logging.error(f"Failed to insert repo {repo.get('full_name')}: {e}")
            print("Couldn't insert records to table.")
            return False

        print(f"Inserted {len(repos)} repos into DB.")
        logging.info(f"Inserted {len(repos)} repos into DB.")
        return True


#Write query functions to pull data for visualization
    def query_repos(self, min_stars=0, language=None, topics=None, pushed_at=None):
        sql = "SELECT * FROM repositories WHERE stargazers_count >= ?"
        params = [min_stars]
        if language:
            sql += " AND language = ?"
            params.append(language)
        if topics:
            sql += " AND topics LIKE ?"
            params.append(f"%{topics}%")
        if pushed_at:
            sql += " AND pushed_at >= ?"
            params.append(pushed_at)

        try:
            df = pd.read_sql_query(sql, self.conn, params=params)
            logging.info(
                f"Queried {len(df)} repos with stars >= {min_stars}" + (f" and language = {language}" if language else ""))
            return df
        except Exception as e:
            logging.error(f"Failed to query repositories: {e}")
            print("Query failed. Check logs for details.")
            return pd.DataFrame()

def run_staging(repos):
    client = GitHubStaging()
    stg_success = client.insert_repos(repos)
    logging.info(f"Staging script closing with status: {stg_success}")
    return stg_success