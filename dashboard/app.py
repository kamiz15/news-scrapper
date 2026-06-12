import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
import streamlit as st

st.set_page_config(
    page_title="Ansu Invest Desktop App",
    page_icon=":ocean:",
    layout="wide",
    initial_sidebar_state="expanded",
)

from dashboard.views import (
    home, hydropower, research, companies, article_detail,
    market_intel, news_trends, sector_compare,
)


def refresh_data():
    progress = st.sidebar.progress(0, text="Starting refresh...")

    def callback(msg, pct):
        progress.progress(min(int(pct), 100), text=msg)

    try:
        from scraper.runner import run_all
        run_all(progress_callback=callback)
        st.sidebar.success("Data refreshed.")
    except Exception as e:
        st.sidebar.error(f"Refresh failed: {e}")
    finally:
        progress.empty()


def main():
    if "page" not in st.session_state:
        st.session_state.page = "Hydropower Dashboard"
    if "view_article" not in st.session_state:
        st.session_state.view_article = None
    if "view_report" not in st.session_state:
        st.session_state.view_report = None

    try:
        if st.session_state.view_article:
            article_detail.show_article()
            return
        if st.session_state.view_report:
            article_detail.show_report()
            return
    except psycopg2.OperationalError as e:
        st.error(f"Cannot connect to the database. Is PostgreSQL running?\n\n{e}")
        return

    st.sidebar.title("Ansu Invest")
    st.sidebar.markdown("---")

    pages = {
        "Hydropower Dashboard": hydropower.show,
        "Market Intelligence": market_intel.show,
        "News Trends": news_trends.show,
        "Sector Comparison": sector_compare.show,
        "Hydro Companies": companies.show,
        "General News": home.show,
        "Expert Research": research.show,
    }

    choice = st.sidebar.radio("Navigation", list(pages.keys()),
                              index=list(pages.keys()).index(st.session_state.page))

    st.session_state.page = choice
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        refresh_data()
        st.rerun()
    st.sidebar.caption("Data from Ansu Invest")

    try:
        pages[choice]()
    except psycopg2.OperationalError as e:
        st.error(f"Cannot connect to the database. Is PostgreSQL running?\n\n{e}")


if __name__ == "__main__":
    main()
