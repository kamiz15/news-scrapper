import streamlit as st
import pandas as pd
from dashboard import data
from dashboard.components.charts import hydro_news_timeline, market_snapshot, research_topics
from config import image_url


def show():
    st.header("Hydropower Dashboard")

    news = data.hydro_news(limit=100)
    research = data.hydro_research(limit=100)
    companies = data.hydro_companies()
    market = data.latest_market()

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
