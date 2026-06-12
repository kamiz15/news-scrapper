import streamlit as st
import pandas as pd
from dashboard import data
from dashboard.components.charts import monthly_news_trend, top_title_terms


def show():
    st.header("News Trends — Hydropower")
    st.markdown("How hydropower coverage evolves and what the market is talking about.")

    monthly = data.monthly_hydro_news()
    titles = data.hydro_titles()

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
    for article in data.hydro_news(limit=15):
        cols = st.columns([5, 1])
        cols[0].markdown(f"**{article['title']}**")
        if article.get("posted_at"):
            cols[0].caption(f"📅 {article['posted_at']}")
        cols[1].button("Read", key=f"trend_{article['article_id']}",
                       on_click=lambda aid=article["article_id"]: setattr(st.session_state, "view_article", aid))
        st.divider()
