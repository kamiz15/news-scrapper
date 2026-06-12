import streamlit as st
from dashboard import data
from config import image_url


def show():
    st.header("Expert Research & Opinions")
    st.markdown("Research reports from Ansu Invest analysts.")

    total = data.research_count()
    hydro_total = data.research_count(hydro_only=True)

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
        reports = data.all_research(per_page, offset)
        for rep in reports:
            with st.container():
                a, b = st.columns([1, 4])
                if rep.get("image"):
                    a.image(image_url(rep["image"]), width=100)
                else:
                    a.markdown("###### :memo:")
                premium = " ⭐" if rep.get("is_premium") else ""
                b.markdown(f"**{rep['title']}**{premium}")
                if rep.get("sub_title"):
                    b.caption(rep["sub_title"])
                tags = []
                if rep.get("is_hydro"):
                    tags.append("🌊 Hydropower")
                if rep.get("posted_at"):
                    tags.append(f"📅 {rep['posted_at']}")
                if tags:
                    b.caption(" | ".join(tags))
                b.button("Read Report", key=f"rread_{rep['expert_id']}",
                         on_click=lambda eid=rep["expert_id"]: setattr(st.session_state, "view_report", eid))
                st.divider()

    with tab2:
        hydro_reports = data.hydro_research(limit=50)
        if hydro_reports:
            for rep in hydro_reports:
                with st.container():
                    a, b = st.columns([1, 4])
                    if rep.get("image"):
                        a.image(image_url(rep["image"]), width=100)
                    else:
                        a.markdown("###### :memo:")
                    premium = " ⭐" if rep.get("is_premium") else ""
                    b.markdown(f"**{rep['title']}**{premium}")
                    if rep.get("sub_title"):
                        b.caption(rep["sub_title"])
                    if rep.get("posted_at"):
                        b.caption(f"📅 {rep['posted_at']}")
                    b.button("Read Report", key=f"hread_{rep['expert_id']}",
                             on_click=lambda eid=rep["expert_id"]: setattr(st.session_state, "view_report", eid))
                    st.divider()
        else:
            st.info("No hydropower research reports yet.")
