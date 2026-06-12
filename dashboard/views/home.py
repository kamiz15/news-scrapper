import streamlit as st
from dashboard import data
from config import clean_html, image_url


def show():
    st.header("General News")
    st.markdown("All articles from Ansu Invest.")

    total_count = data.news_count()
    categories = data.news_category_counts()

    col1, col2 = st.columns([1, 3])
    col1.metric("Total Articles", total_count)
    col2.metric("Categories", len(categories))

    if "news_category" not in st.session_state:
        st.session_state.news_category = "All"
    if "news_page" not in st.session_state:
        st.session_state.news_page = 0

    cat_names = ["All"] + [c[0] for c in categories if c[0]]
    cols = st.columns(6)
    for i, cat in enumerate(cat_names[:6]):
        with cols[i]:
            if st.button(cat, key=f"ncat_{cat}", use_container_width=True,
                         type="primary" if st.session_state.news_category == cat else "secondary"):
                st.session_state.news_category = cat
                st.session_state.news_page = 0
                st.rerun()

    per_page = 15
    offset = st.session_state.news_page * per_page

    if st.session_state.news_category == "All":
        articles = data.all_news(per_page, offset)
        count = total_count
    else:
        articles = data.news_by_category(st.session_state.news_category, per_page, offset)
        count = data.news_count_by_category(st.session_state.news_category)

    if articles:
        for article in articles:
            with st.container():
                a, b = st.columns([1, 4])
                if article.get("image"):
                    a.image(image_url(article["image"]), width=120)
                else:
                    a.markdown("###### :newspaper:")
                b.markdown(f"**{article['title']}**")
                if article.get("sub_title"):
                    b.caption(article["sub_title"])
                if article.get("summary"):
                    b.write(clean_html(article["summary"])[:300] + "...")
                tags = []
                if article.get("category"):
                    tags.append(f"📌 {article['category']}")
                if article.get("is_hydro"):
                    tags.append("🌊 Hydropower")
                if article.get("posted_at"):
                    tags.append(f"📅 {article['posted_at']}")
                if tags:
                    b.caption(" | ".join(tags))
                b.button("Read More", key=f"read_{article['article_id']}",
                         on_click=lambda aid=article["article_id"]: setattr(st.session_state, "view_article", aid))
                st.divider()

        col_l, _, col_r = st.columns([1, 2, 1])
        with col_l:
            if st.button("← Previous", disabled=st.session_state.news_page == 0):
                st.session_state.news_page -= 1
                st.rerun()
        with col_r:
            max_pg = max(0, (count - 1) // per_page)
            if st.button("Next →", disabled=st.session_state.news_page >= max_pg):
                st.session_state.news_page += 1
                st.rerun()
    else:
        st.info("No articles found.")
