import streamlit as st
import pandas as pd
from database.connection import get_conn, release_conn
from database.repository import get_all_hydro_companies, get_latest_market_data


def show():
    st.header(":office: Hydropower Companies")
    st.markdown("Listed hydropower companies and their latest market data.")

    conn = get_conn()
    try:
        companies = get_all_hydro_companies(conn)
        market = get_latest_market_data(conn)

        if companies:
            comp_df = pd.DataFrame(companies)
            st.subheader(f"Total: {len(companies)} companies")
            st.dataframe(comp_df, use_container_width=True)
        else:
            st.info("No company data yet. Run the scraper first.")

        st.subheader("Latest Market Data")
        if market:
            market_df = pd.DataFrame(market)
            market_df = market_df.rename(columns={
                "company_name": "Company", "ltp": "LTP (NPR)",
                "point_change": "Change", "percent_change": "% Change",
                "volume": "Volume"
            })
            st.dataframe(market_df, use_container_width=True)
        else:
            st.info("No market data yet.")

    finally:
        release_conn(conn)
