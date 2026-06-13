import streamlit as st
import pandas as pd
from dashboard import data
from dashboard.components.charts import hydro_news_timeline, market_snapshot, research_topics
from dashboard.ai_insights import market_brief, news_impact_analysis, sector_pulse
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

    if market:
        market_df = pd.DataFrame(market)
        with st.container(border=True):
            st.subheader("AI Market Brief")
            with st.spinner("Generating market summary..."):
                brief = market_brief(market_df)
            st.markdown(brief)
            st.caption("Auto-generated from latest market data")
    else:
        st.info("No market data yet.")

    st.subheader("Market Snapshot")
    if market:
        fig = market_snapshot(market_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

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

    if news and market:
        if st.button("Analyze News Impact on Market", use_container_width=True, type="primary"):
            with st.spinner("Analyzing recent news and market data..."):
                analysis = news_impact_analysis(news_df, market_df)
            st.info(analysis)

    with st.expander("Sector Pulse — Themes & Sentiment", expanded=False):
        if news:
            with st.spinner("Analyzing sector pulse..."):
                pulse = sector_pulse(news_df)
            sentiment = pulse.get("overall_sentiment", "neutral")
            emoji = {"positive": "🟢", "neutral": "🟡", "negative": "🔴"}
            st.metric("Overall Sentiment", f"{emoji.get(sentiment, '🟡')} {sentiment.title()}")
            themes = pulse.get("key_themes", [])
            if themes:
                st.write("**Key Themes:**")
                cols = st.columns(len(themes))
                for i, theme in enumerate(themes):
                    cols[i if i < len(cols) else i % len(cols)].markdown(f"- {theme}")
            rec_ids = pulse.get("article_ids_recommended", [])
            if rec_ids:
                st.write("**Recommended Reads:**")
                for rec_id in rec_ids:
                    match = [a for a in news if a.get("article_id") == rec_id]
                    if match:
                        a = match[0]
                        st.markdown(f"- [{a['title']}](https://ansuinvest.com/news/detail/{a.get('slug', '')})")
        else:
            st.info("No news data to analyze.")

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
