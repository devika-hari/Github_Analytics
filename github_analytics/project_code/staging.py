import sqlite3
import logging
import pandas as pd

logger = logging.getLogger("git_analytics")

class GitHubStaging:
    def __init__(self, db_path="github_repos.db"):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
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
                conn.commit()
                logger.info("DDL for table creation ran successfully.")
        except sqlite3.Error as e:
            logger.error(f"Failed to create tables: {e}")
            print("Table creation failed. Check logs for details.")


    def insert_repos(self, repos):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                for repo in repos:
                    topics = ",".join(repo.get("topics", []))
                    cursor.execute("""
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
                conn.commit()
                logger.info(f"Inserted {len(repos)} repos into DB.")
                return True
        except Exception as e:
            logger.error(f"Insert operation failed: {e}")
            return False

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
            with self._connect() as conn:
                df = pd.read_sql_query(sql, conn, params=params)
                logger.info(
                    f"Queried {len(df)} repos with stars >= {min_stars}" + (f" and language = {language}" if language else ""))
                return df
        except Exception as e:
            logger.error(f"Failed to query repositories: {e}")
            print("Query failed. Check logs for details.")
            return pd.DataFrame()

def run_staging(repos):
    ddl = GitHubStaging()
    ddl._create_tables()
    stg_success = ddl.insert_repos(repos)
    logger.info(f"Staging script closing with status: {stg_success}")
    return stg_success