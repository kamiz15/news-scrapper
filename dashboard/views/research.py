import streamlit as st
from database.connection import get_conn, release_conn
from database.repository import get_all_research, get_all_research_count, get_hydro_research
from config import image_url


def show():
    st.header("Expert Research & Opinions")
    st.markdown("Research reports from Ansu Invest analysts.")

    conn = get_conn()
    try:
        total = get_all_research_count(conn)
        hydro_total = get_all_research_count(conn, hydro_only=True)

        col1, col2 = st.columns(2)
        col1.metric("Total Reports", total)
        col2.metric("Hydropower Reports", hydro_total)

        tab1, tab2 = st.tabs(["All Research", "Hydropower Only"])

        per_page = 15
        if "research_page" not in st.session_state:
            st.session_state.research_page = 0

        with tab1:
            col_l, _, col_r = st.columns([1, 2, 1])
            with col_l:
                if st.button("← Previous", key="rp_prev", disabled=st.session_state.research_page == 0):
                    st.session_state.research_page -= 1
                    st.rerun()
            with col_r:
                max_pg = max(0, (total - 1) // per_page)
                if st.button("Next →", key="rp_next", disabled=st.session_state.research_page >= max_pg):
                    st.session_state.research_page += 1
                    st.rerun()

            offset = st.session_state.research_page * per_page
            reports = get_all_research(conn, limit=per_page, offset=offset)
            for report in reports:
                with st.container():
                    a, b = st.columns([1, 4])
                    if report.get("image"):
                        a.image(image_url(report["image"]), width=100)
                    else:
                        a.markdown("###### :memo:")
                    premium = " ⭐" if report.get("is_premium") else ""
                    b.markdown(f"**{report['title']}**{premium}")
                    if report.get("sub_title"):
                        b.caption(report["sub_title"])
                    tags = []
                    if report.get("is_hydro"):
                        tags.append("🌊 Hydropower")
                    if report.get("posted_at"):
                        tags.append(f"📅 {report['posted_at']}")
                    if tags:
                        b.caption(" | ".join(tags))
                    b.button("Read Report", key=f"rread_{report['expert_id']}",
                             on_click=lambda eid=report["expert_id"]: setattr(st.session_state, "view_report", eid))
                    st.divider()

        with tab2:
            if st.button("← Back", key="hydro_back"):
                st.session_state.research_page = 0
                st.rerun()
            hydro_reports = get_hydro_research(conn, limit=50)
            if hydro_reports:
                for report in hydro_reports:
                    with st.container():
                        a, b = st.columns([1, 4])
                        if report.get("image"):
                            a.image(image_url(report["image"]), width=100)
                        else:
                            a.markdown("###### :memo:")
                        premium = " ⭐" if report.get("is_premium") else ""
                        b.markdown(f"**{report['title']}**{premium}")
                        if report.get("sub_title"):
                            b.caption(report["sub_title"])
                        if report.get("posted_at"):
                            b.caption(f"📅 {report['posted_at']}")
                        b.button("Read Report", key=f"hread_{report['expert_id']}",
                                 on_click=lambda eid=report["expert_id"]: setattr(st.session_state, "view_report", eid))
                        st.divider()
            else:
                st.info("No hydropower research reports yet.")

    finally:
        release_conn(conn)
