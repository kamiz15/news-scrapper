import streamlit as st
import pandas as pd
from database.connection import get_conn, release_conn
from database.repository import get_sector_market_stats
from dashboard.components.charts import sector_performance, sector_volume


def show():
    st.header("Sector Comparison")
    st.markdown("How the hydropower sector performs against the rest of the market.")

    conn = get_conn()
    try:
        stats = get_sector_market_stats(conn)

        if not stats:
            st.warning(
                "No sector data yet. Click 'Refresh Data' in the sidebar "
                "to fetch companies and market data."
            )
            return

        df = pd.DataFrame(stats)
        df["avg_percent_change"] = pd.to_numeric(df["avg_percent_change"], errors="coerce")

        hydro_rows = df[df["sector"].str.contains("hydro|power", case=False, na=False)]
        col1, col2 = st.columns(2)
        col1.metric("Sectors Tracked", len(df))
        if not hydro_rows.empty:
            avg = hydro_rows["avg_percent_change"].mean()
            col2.metric("Hydro Sector Avg % Change", f"{avg:+.2f}%")

        fig = sector_performance(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        fig = sector_volume(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Sector Table")
        table = df.rename(columns={
            "sector": "Sector", "companies": "Companies",
            "avg_percent_change": "Avg % Change", "total_volume": "Total Volume",
        })
        st.dataframe(table, use_container_width=True, hide_index=True)

    finally:
        release_conn(conn)
