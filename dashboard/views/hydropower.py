import streamlit as st
import pandas as pd
from database.connection import get_conn, release_conn
from database.repository import (
    get_hydro_news, get_hydro_research,
    get_all_hydro_companies, get_latest_market_data,
)
from dashboard.components.charts import hydro_news_timeline, market_snapshot, research_topics
from config import image_url


def show():
    st.header("Hydropower Dashboard")

    conn = get_conn()
    try:
        news = get_hydro_news(conn, limit=100)
        research = get_hydro_research(conn, limit=100)
        companies = get_all_hydro_companies(conn)
        market = get_latest_market_data(conn)

        col1, col2, col3 = st.columns(3)
        col1.metric("News Articles", len(news))
        col2.metric("Research Reports", len(research))
        col3.metric("Hydro Companies", len(companies))

        st.subheader("Market Snapshot")
        if market:
            market_df = pd.DataFrame(market)
            fig = market_snapshot(market_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No market data yet.")

        st.subheader("News Timeline")
        if news:
            news_df = pd.DataFrame(news)
            fig = hydro_news_timeline(news_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("Research Topics")
        if research:
            research_df = pd.DataFrame(research)
            fig = research_topics(research_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("Latest Hydro News")
        if news:
            for article in news[:10]:
                with st.container():
                    a, b = st.columns([1, 4])
                    if article.get("image"):
                        a.image(image_url(article["image"]), width=100)
                    else:
                        a.markdown("###### :newspaper:")
                    b.markdown(f"**{article['title']}**")
                    b.caption(f"📅 {article.get('posted_at', '')}")
                    b.button("Read", key=f"hnews_{article['article_id']}",
                             on_click=lambda aid=article["article_id"]: setattr(st.session_state, "view_article", aid))
                    st.divider()

        st.subheader("Hydro Companies")
        if companies:
            comp_df = pd.DataFrame(companies)
            st.dataframe(comp_df, use_container_width=True)

    finally:
        release_conn(conn)
