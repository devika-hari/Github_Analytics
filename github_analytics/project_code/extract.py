import logging
import requests
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

logger = logging.getLogger("git_analytics")

class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        load_dotenv()
        self.token = os.getenv("GITHUB_TOKEN")

        if not self.token:
            logger.error("GITHUB_TOKEN is missing in .env file")
            print("Please ensure right GITHUB TOKEN is placed in .env file and re-run.")
            raise ValueError("GITHUB_TOKEN missing in .env file")

        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json"
        }

    def _get(self, endpoint, params=None):
        params = params or {}
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            logger.info(f"GitHub API response {response.status_code} for URL: {url}")
            return response.json()

        logger.error(f"GitHub API Error {response.status_code} for URL: {url}")
        logger.error(f"Response: {response.text}")

        if response.status_code == 403 and "rate limit" in response.text.lower():
            print("GitHub API rate limit reached. Please try again later.")
            print(f"Remaining: {response.headers.get('X-RateLimit-Remaining')}")
            print(f"Resets at: {response.headers.get('X-RateLimit-Reset')}")
        return None

    def _paginate(self, endpoint, params, max_pages):
        all_items = []
        local_params = params.copy()
        for page in range(1, max_pages + 1):
            local_params["page"] = page
            data = self._get(endpoint, local_params)

            if not data or "items" not in data or len(data["items"]) == 0:
                logger.warning(f"No data/items on page {page}. Stopping.")
                break
            logger.info(f"Fetched page {page} with {len(data['items'])} repos")
            all_items.extend(data["items"])
        return all_items

    def search_repositories(self, query, sort, order, per_page, max_pages):
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page
        }
        repos = self._paginate("/search/repositories", params, max_pages=max_pages)
        return repos

    def fetch_top_repos_last_n_days(self, no_of_days,min_stars,sort,order,per_page,max_pages):
        today = datetime.today()
        date_n = today - timedelta(days=no_of_days)
        formatted_date = date_n.strftime("%Y-%m-%d")
        print(f"Preparing to fetch repositories updated after {formatted_date} with more than {min_stars} stars...")
        logger.info(f"Preparing fetch for repos after {formatted_date} with more than {min_stars} stars.")
        query_string = f"pushed:>{formatted_date} stars:>{min_stars}"
        repos = self.search_repositories(query_string, sort, order,per_page, max_pages)
        if not repos:
            print("Fetching repositories failed.")
            logger.warning("Fetching repositories failed or No repositories returned by GitHub")
            return []

        print(f"Fetched {len(repos)} repos")
        logger.info(f"Fetched {len(repos)} repos.")
        return repos


def run_extract(no_of_days=30,min_stars=200,max_pages=3,sort="stars",order="desc",per_page=30):
    client = GitHubClient()
    repos = client.fetch_top_repos_last_n_days(no_of_days,min_stars,sort,order,per_page, max_pages)
    return repos

