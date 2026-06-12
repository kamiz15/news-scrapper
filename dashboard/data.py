"""Cached data access for the dashboard.

Every read goes through st.cache_data so page switches don't re-query the
database. The cache is cleared by the sidebar Refresh Data button; otherwise
entries expire after an hour.
"""
import streamlit as st
from database.connection import get_conn, release_conn
from database import repository as repo

_TTL = 3600  # seconds


def _run(fn, *args, **kwargs):
    conn = get_conn()
    try:
        return fn(conn, *args, **kwargs)
    finally:
        release_conn(conn)


@st.cache_data(ttl=_TTL, show_spinner=False)
def all_news(limit, offset):
    return _run(repo.get_all_news, limit=limit, offset=offset)


@st.cache_data(ttl=_TTL, show_spinner=False)
def news_count(hydro_only=False):
    return _run(repo.get_all_news_count, hydro_only=hydro_only)


@st.cache_data(ttl=_TTL, show_spinner=False)
def news_by_category(category, limit, offset):
    return _run(repo.get_news_by_category, category, limit=limit, offset=offset)


@st.cache_data(ttl=_TTL, show_spinner=False)
def news_count_by_category(category):
    return _run(repo.get_news_count_by_category, category)


@st.cache_data(ttl=_TTL, show_spinner=False)
def news_category_counts():
    return _run(repo.get_news_category_counts)


@st.cache_data(ttl=_TTL, show_spinner=False)
def hydro_news(limit=20):
    return _run(repo.get_hydro_news, limit=limit)


@st.cache_data(ttl=_TTL, show_spinner=False)
def hydro_research(limit=20):
    return _run(repo.get_hydro_research, limit=limit)


@st.cache_data(ttl=_TTL, show_spinner=False)
def all_research(limit, offset):
    return _run(repo.get_all_research, limit=limit, offset=offset)


@st.cache_data(ttl=_TTL, show_spinner=False)
def research_count(hydro_only=False):
    return _run(repo.get_all_research_count, hydro_only=hydro_only)


@st.cache_data(ttl=_TTL, show_spinner=False)
def hydro_companies():
    return _run(repo.get_all_hydro_companies)


@st.cache_data(ttl=_TTL, show_spinner=False)
def latest_market(limit=50):
    return _run(repo.get_latest_market_data, limit=limit)


@st.cache_data(ttl=_TTL, show_spinner=False)
def hydro_market():
    return _run(repo.get_hydro_market_data)


@st.cache_data(ttl=_TTL, show_spinner=False)
def sector_stats():
    return _run(repo.get_sector_market_stats)


@st.cache_data(ttl=_TTL, show_spinner=False)
def monthly_hydro_news():
    return _run(repo.get_monthly_hydro_news_counts)


@st.cache_data(ttl=_TTL, show_spinner=False)
def hydro_titles(limit=2000):
    return _run(repo.get_hydro_news_titles, limit=limit)


@st.cache_data(ttl=_TTL, show_spinner=False)
def article(article_id):
    return _run(repo.get_article_by_article_id, article_id)


@st.cache_data(ttl=_TTL, show_spinner=False)
def report(expert_id):
    return _run(repo.get_report_by_expert_id, expert_id)
