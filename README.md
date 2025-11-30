📊 **GitHub Repositories Analytics**


A Python-based analytics tool to fetch, store, and visualize trending GitHub repositories using the GitHub REST API.
The project includes:
  1. Data Extraction from GitHub API
  2. Staging Layer using SQLite
  3. Interactive Dashboard built with Streamlit 



🗂 **Project Structure**

GitHub_Analytics/

    |--- README.md
    |
    |--- project_code/
        ├── main.py
        ├── extract.py
        ├── staging.py
        ├── dashboard.py
        ├── config.py
        ├── .env
        └── requirements.txt

All source code and modules are placed in the project_code/ folder.

🔧 **Prerequisites & Installing Dependencies**

    1. Please refer to requirements.txt for all packages to be installed.
       Inside project_code/:
          pip install -r requirements.txt
    
    2. GitHub personal access token (PAT)

🔐 **1. Environment Setup**

Place the generated GitHub token in .env file inside project_code/:
  GITHUB_TOKEN=your_github_token_here

To generate a token:
Login to GitHub
Go to Settings → Developer settings → Personal access tokens → Tokens (classic)
Click Generate new token
Copy the token and paste it into .env


⚙️ **2. Configure Fetch Settings (config.py)**

Inside project_code/config.py, update the below parameters which will define the conditions for data - fetch using API.

         no_of_days    --> Number of past days to consider when fetching repositories
        
         min_stars      --> Minimum stars threshold
          
          max_pages       --> Number of API pages (max 1000 repos)
          
          per_page        --> Results per page
          
          sort           --> GitHub sort key (e.g., stars)
          
          order           --> "asc" or "desc" ,the sort order

GitHub API limitation: Maximum 1000 items can be fetched per query.

▶️ **3. Run Extraction & Staging**

From inside project root:

      cd project_code
      python main.py

On success, repositories will be stored in github_repos.db (SQLite).

📈 **4. Launch the Streamlit Dashboard**

  **Run:**
  streamlit run dashboard.py

This will automatically open:
http://localhost:8501/

The dashboard lets you:
  1. Filter repos by stars, languages, topics, and recent activity (based on pushed_at)
  2. View charts:
  Top repos by stars
  Top repos by forks
  Popular programming languages
  Trending topics

**Closing the Dashboard**

To shut down Streamlit:
  Press Ctrl + C in the terminal

📝 **Logging**

Two separate log files are created, stored automatically inside project_code/.

    1. git_analytics.log (main ETL pipeline)
    2. git_dashboard.log (dashboard activity)

🖼️ **Dashboard Preview**

<img width="1214" height="727" alt="image" src="https://github.com/user-attachments/assets/c09819f8-08c9-4cc5-96ec-4e890c534263" />

