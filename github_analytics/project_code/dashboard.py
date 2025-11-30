import streamlit as st
import pandas as pd
import plotly.express as px
from staging import GitHubStaging
from datetime import datetime, timedelta
import logging

logging.basicConfig(
    filename="../git_dashboard.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("git_dashboard")
logger.info("Dashboard opening ...")

staging_client = GitHubStaging()


days_filter = st.sidebar.selectbox(
    "Repositories updated in the last N days",
    options=[7, 14, 30],
    index=2
)

# Fetch distinct languages and topics from DB for filters
def get_distinct_languages(client):
    df = client.query_repos()
    languages = df['language'].dropna().unique().tolist()
    languages.sort()
    return languages

def get_distinct_topics(client):
    df = client.query_repos()
    all_topics = df['topics'].dropna().str.split(',').explode().unique().tolist()
    all_topics.sort()
    return all_topics

languages = get_distinct_languages(staging_client)
topics = get_distinct_topics(staging_client)
logger.info("Fetched filter information")
language_filter = st.sidebar.selectbox("Programming Language", options=["All"] + languages)
topic_filter = st.sidebar.selectbox("Topic", options=["All"] + topics)

# Convert "All" to None
language_filter = None if language_filter == "All" else language_filter
topic_filter = None if topic_filter == "All" else topic_filter

#fetch data
pushed_date = (datetime.today() - timedelta(days=days_filter)).strftime("%Y-%m-%d")
df = staging_client.query_repos(
    min_stars=0,
    language=language_filter,
    topics=topic_filter,
    pushed_at=pushed_date
)
logger.info("Fetched data for dashboard")

st.title("GitHub Repositories Analytics Dashboard")

# Display summary
st.write(f"Total repositories fetched: {len(df)}")
st.write(f"Criteria: Top {len(df)} by stars in last {days_filter} days, "
         f"Language: {language_filter or 'All'}, Topic: {topic_filter or 'All'}")

#Top 10 repos by stars
st.subheader("Top 10 Repositories by Stars")
if not df.empty:
    top_stars = df.nlargest(10, 'stargazers_count')
    fig1 = px.bar(top_stars, x='full_name', y='stargazers_count',
                  labels={
                      "full_name": "Repository",
                      "stargazers_count": "Stars"
                  },
                  hover_data=['forks_count', 'language'],
                  title='Top 10 Repositories by Stars')
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.write("No data available for this filter combination.")

# Top 10 repos by forks
st.subheader("Top 10 Repositories by Forks")
if not df.empty:
    top_forks = df.nlargest(10, 'forks_count')
    fig2 = px.bar(top_forks, x='full_name', y='forks_count',
                  labels={
                      "full_name": "Repository",
                      "forks_count": "Forks"
                  },
                  hover_data=['stargazers_count', 'language'],
                  title='Top 10 Repositories by Forks')
    st.plotly_chart(fig2, use_container_width=True)

# Most popular programming languages (Top 10)
st.subheader("Most Popular Programming Languages (Top 10)")
if not df.empty:
    lang_counts = df['language'].value_counts().nlargest(10).reset_index()
    lang_counts.columns = ['language', 'count']
    fig3 = px.pie(lang_counts, values='count', names='language', title='Popular Languages (Top 10)')
    st.plotly_chart(fig3, use_container_width=True)

# Top Performing Topics
st.subheader("Top Performing Topics")
if not df.empty:
    topics_series = df['topics'].dropna().str.split(',').explode()
    top_topics = topics_series.value_counts().nlargest(10).reset_index()
    top_topics.columns = ['topic', 'count']
    fig4 = px.bar(top_topics, x='topic', y='count', title='Top 10 Topics by Repo Count')
    st.plotly_chart(fig4, use_container_width=True)
