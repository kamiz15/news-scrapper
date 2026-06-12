import streamlit as st
from dashboard.chat_engine import retrieve, generate_answer


def show():
    st.header("Chat with Articles")
    st.caption("Ask questions about news articles and research reports.")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_sources" not in st.session_state:
        st.session_state.chat_sources = {}

    with st.expander("What can I ask?", expanded=False):
        st.markdown("""
- *"What recent articles cover hydropower projects in Nepal?"*
- *"Tell me about the Sanigad hydropower project."*
- *"Which companies are involved in the energy sector?"*
- *"Summarize the latest market trends."*

The assistant answers based on scraped articles. It will tell you when it doesn't have enough information.
""")

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("Sources", expanded=False):
                    for s in msg["sources"]:
                        slug = s.get("slug", "")
                        if slug:
                            st.markdown(f"- [{s['title']}](https://ansuinvest.com/news/detail/{slug})")
                        else:
                            st.markdown(f"- {s['title']}")

    if prompt := st.chat_input("Ask a question about the articles..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching articles..."):
                chunks = retrieve(prompt)
                answer, sources = generate_answer(prompt, chunks, st.session_state.chat_messages)

            st.markdown(answer)
            if sources:
                with st.expander("Sources", expanded=True):
                    for s in sources:
                        slug = s.get("slug", "")
                        if slug:
                            st.markdown(f"- [{s['title']}](https://ansuinvest.com/news/detail/{slug})")
                        else:
                            st.markdown(f"- {s['title']}")

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
        })

    if st.session_state.chat_messages:
        if st.button("Clear conversation"):
            st.session_state.chat_messages = []
            st.session_state.chat_sources = {}
            st.rerun()
