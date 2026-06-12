import streamlit as st
import pandas as pd
from database.connection import get_conn, release_conn
from database.repository import get_hydro_market_data
from dashboard.components.charts import top_movers, volume_leaders


def show():
    st.header("Market Intelligence — Hydropower")
    st.markdown("Latest market data for listed hydropower companies (your competitors).")

    conn = get_conn()
    try:
        market = get_hydro_market_data(conn)

        if not market:
            st.warning(
                "No market data matched hydro companies yet. "
                "Click 'Refresh Data' in the sidebar to fetch the latest snapshot."
            )
            return

        df = pd.DataFrame(market)
        df["percent_change"] = pd.to_numeric(df["percent_change"], errors="coerce")

        gainers = int((df["percent_change"] > 0).sum())
        losers = int((df["percent_change"] < 0).sum())
        col1, col2, col3 = st.columns(3)
        col1.metric("Hydro Companies Traded", len(df))
        col2.metric("Gainers", gainers)
        col3.metric("Losers", losers)

        fig = top_movers(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        fig = volume_leaders(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("All Hydro Companies — Latest Prices")
        table = df.rename(columns={
            "company_name": "Company", "symbol": "Symbol", "sector": "Sector",
            "ltp": "LTP (NPR)", "point_change": "Change",
            "percent_change": "% Change", "volume": "Volume",
            "timestamp": "As Of",
        })
        st.dataframe(table, use_container_width=True, hide_index=True)

    finally:
        release_conn(conn)
