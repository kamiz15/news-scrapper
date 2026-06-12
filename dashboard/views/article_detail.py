import streamlit as st
from database.connection import get_conn, release_conn
from database.repository import get_article_by_article_id, get_report_by_expert_id
from config import clean_html, image_url


def show_article():
    article_id = st.session_state.view_article
    conn = get_conn()
    try:
        article = get_article_by_article_id(conn, article_id)
        if not article:
            st.error("Article not found.")
            if st.button("Back to News"):
                st.session_state.view_article = None
                st.rerun()
            return

        st.button("← Back to News", on_click=lambda: setattr(st.session_state, "view_article", None))
        st.title(article["title"])
        if article.get("sub_title"):
            st.subheader(article["sub_title"])
        if article.get("image"):
            st.image(image_url(article["image"]))
        if article.get("posted_at"):
            st.caption(f"Published: {article['posted_at']}")
        if article.get("category"):
            st.caption(f"Category: {article['category']}")
        st.divider()
        if article.get("summary"):
            st.markdown(clean_html(article["summary"]))
        else:
            st.info("No content available for this article.")

    finally:
        release_conn(conn)


def show_report():
    expert_id = st.session_state.view_report
    conn = get_conn()
    try:
        report = get_report_by_expert_id(conn, expert_id)
        if not report:
            st.error("Report not found.")
            if st.button("Back to Research"):
                st.session_state.view_report = None
                st.rerun()
            return

        st.button("← Back to Research", on_click=lambda: setattr(st.session_state, "view_report", None))
        premium = " ⭐ PREMIUM" if report.get("is_premium") else ""
        st.title(f"{report['title']}{premium}")
        if report.get("sub_title"):
            st.subheader(report["sub_title"])
        if report.get("image"):
            st.image(image_url(report["image"]))
        if report.get("posted_at"):
            st.caption(f"Published: {report['posted_at']}")
        st.divider()
        if report.get("summary"):
            st.markdown(clean_html(report["summary"]))
        else:
            st.info("No content available for this report.")

    finally:
        release_conn(conn)
