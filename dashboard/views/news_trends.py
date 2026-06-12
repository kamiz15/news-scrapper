import streamlit as st
import pandas as pd
from database.connection import get_conn, release_conn
from database.repository import (
    get_monthly_hydro_news_counts, get_hydro_news_titles, get_hydro_news,
)
from dashboard.components.charts import monthly_news_trend, top_title_terms


def show():
    st.header("News Trends — Hydropower")
    st.markdown("How hydropower coverage evolves and what the market is talking about.")

    conn = get_conn()
    try:
        monthly = get_monthly_hydro_news_counts(conn)
        titles = get_hydro_news_titles(conn)

        if not monthly and not titles:
            st.warning(
                "No hydro news in the database yet. "
                "Click 'Refresh Data' in the sidebar to fetch articles."
            )
            return

        if monthly:
            fig = monthly_news_trend(pd.DataFrame(monthly))
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        if titles:
            fig = top_title_terms(titles)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("Latest Hydro Headlines")
        for article in get_hydro_news(conn, limit=15):
            cols = st.columns([5, 1])
            cols[0].markdown(f"**{article['title']}**")
            if article.get("posted_at"):
                cols[0].caption(f"📅 {article['posted_at']}")
            cols[1].button("Read", key=f"trend_{article['article_id']}",
                           on_click=lambda aid=article["article_id"]: setattr(st.session_state, "view_article", aid))
            st.divider()

    finally:
        release_conn(conn)
