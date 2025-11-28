import logging
import requests
from dotenv import load_dotenv #loads .env file
import os #reads token from environment
from datetime import datetime, timedelta

logging.basicConfig(
    filename="extract.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__) #returns the same logger object if it already exists.

#Fetch Top-starred public GitHub repositories that were updated in the last 30 days.
class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self): #token, header
        load_dotenv()  # load .env file
        self.token = os.getenv("GITHUB_TOKEN")  # Read GitHub token

        if not self.token: # validate token
            logging.error("GITHUB_TOKEN is missing in .env file")
            raise ValueError("GITHUB_TOKEN is missing in .env file")
        self.headers = { # Prepare API headers
            "Authorization": f"token {self.token}",   #your token
            "Accept": "application/vnd.github+json"   #tell git to send the response in the official GitHub JSON format.
        }
#revisit for error handling
    def _get(self, endpoint, params=None): #Actual get request based on passed query parameters - reusable
        params = params or {} #prevents passing None to requests.get
        url = f"{self.BASE_URL}{endpoint}" #not obj/class variables, local var to this fn - Storing it in self can cause bugs if multiple requests happen
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            logging.info(f"GitHub API response {response.status_code} for URL: {url}")
            return response.json()
        else:
            logging.error(f"GitHub API Error {response.status_code} for URL: {url}")
            logging.error(f"Response: {response.text}")
            print(f"GitHub API Error {response.status_code}: {response.text}")

            if response.status_code == 403: #RateLimit hit
                if "rate limit" in response.text.lower():
                    print("GitHub API rate limit reached. Please try again later.")
                    remaining = response.headers.get("X-RateLimit-Remaining")
                    reset = response.headers.get("X-RateLimit-Reset")
                    print(f"Remaining: {remaining}, resets at: {reset}")
            return None



    def _paginate(self, endpoint, params, max_pages):
        #GitHub Search API returns max 100 items per page, we need to fetch multiple pgs - 2 means 200, 3 means 300...
        all_items = []
        local_params = params.copy()
        for page in range(1, max_pages + 1):
            local_params["page"] = page #appending page key in params dict, updates which page we are fetching in the current iteration of the loop
            data = self._get(endpoint, local_params) #calling above get function for each page
            logging.info(f"Fetched page {page} with {len(data['items'])} repos")
            if not data or "items" not in data or len(data["items"]) == 0:
                break  # no more results
            all_items.extend(data["items"]) #data["items"]-list of repos, all_items -cum list - combining pages into one flat list (extend vs append)
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
        print(f"Fetching repositories updated after {formatted_date} with more than {min_stars} stars...")
        logging.info(f"Starting fetch for repos after {formatted_date} with more than {min_stars} stars.")

        query_string = f"pushed:>{formatted_date} stars:>{min_stars}"
        repos = self.search_repositories(query_string, sort, order,per_page, max_pages)
        if not repos:
            print("No repositories found.")
            logging.warning("No repositories returned by GitHub")
            return []

        print(f"Fetched {len(repos)} repos")
        logging.info(f"Fetched {len(repos)} repos.")
        return repos


def run_extract(no_of_days=30,min_stars=200,max_pages=3,sort="stars",order="desc",per_page=30):
    client = GitHubClient()
    repos = client.fetch_top_repos_last_n_days(no_of_days,min_stars,sort,order,per_page, max_pages)
    return repos

