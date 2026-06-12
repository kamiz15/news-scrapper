import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def hydro_news_timeline(news_df: pd.DataFrame):
    if news_df.empty:
        return None
    df = news_df.copy()
    df["posted_at"] = pd.to_datetime(df["posted_at"], errors="coerce")
    df = df.dropna(subset=["posted_at"])
    df["date"] = df["posted_at"].dt.date
    daily = df.groupby("date").size().reset_index(name="count")
    fig = px.bar(daily, x="date", y="count",
                 title="Hydro News Over Time",
                 labels={"date": "Date", "count": "Articles"},
                 color_discrete_sequence=["#1f77b4"])
    return fig


def market_snapshot(market_df: pd.DataFrame):
    if market_df.empty:
        return None
    df = market_df.copy()
    df["ltp"] = pd.to_numeric(df["ltp"], errors="coerce")
    df["percent_change"] = pd.to_numeric(df["percent_change"], errors="coerce")
    df = df.dropna(subset=["ltp"])
    fig = px.bar(df.head(15), x="company_name", y="ltp",
                 title="Latest Traded Prices (All Companies)",
                 labels={"company_name": "Company", "ltp": "LTP (NPR)"},
                 color="percent_change", color_continuous_scale="RdYlGn")
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def top_movers(market_df: pd.DataFrame, n=10):
    """Top gainers and losers by % change (horizontal bar)."""
    if market_df.empty:
        return None
    df = market_df.copy()
    df["percent_change"] = pd.to_numeric(df["percent_change"], errors="coerce")
    df = df.dropna(subset=["percent_change"]).sort_values("percent_change")
    movers = pd.concat([df.head(n), df.tail(n)]).drop_duplicates()
    if movers.empty:
        return None
    fig = px.bar(movers, x="percent_change", y="company_name", orientation="h",
                 title=f"Top Movers (best/worst {n} by % change)",
                 labels={"company_name": "", "percent_change": "% Change"},
                 color="percent_change", color_continuous_scale="RdYlGn")
    fig.update_layout(height=max(400, 28 * len(movers)), showlegend=False)
    return fig


def volume_leaders(market_df: pd.DataFrame, n=10):
    if market_df.empty:
        return None
    df = market_df.copy()
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    df = df.dropna(subset=["volume"]).nlargest(n, "volume")
    if df.empty:
        return None
    fig = px.bar(df, x="company_name", y="volume",
                 title=f"Volume Leaders (top {n})",
                 labels={"company_name": "Company", "volume": "Volume"},
                 color_discrete_sequence=["#f79920"])
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def monthly_news_trend(monthly_df: pd.DataFrame):
    if monthly_df.empty:
        return None
    df = monthly_df.copy()
    df["month"] = pd.to_datetime(df["month"], errors="coerce")
    df = df.dropna(subset=["month"])
    fig = px.line(df, x="month", y="count", markers=True,
                  title="Hydropower News Coverage by Month",
                  labels={"month": "Month", "count": "Articles"})
    return fig


def sector_performance(sector_df: pd.DataFrame):
    if sector_df.empty:
        return None
    df = sector_df.copy()
    df["avg_percent_change"] = pd.to_numeric(df["avg_percent_change"], errors="coerce")
    df = df.dropna(subset=["avg_percent_change"]).sort_values("avg_percent_change")
    fig = px.bar(df, x="avg_percent_change", y="sector", orientation="h",
                 title="Average % Change by Sector (latest snapshot)",
                 labels={"sector": "", "avg_percent_change": "Avg % Change"},
                 color="avg_percent_change", color_continuous_scale="RdYlGn")
    fig.update_layout(showlegend=False)
    return fig


def sector_volume(sector_df: pd.DataFrame):
    if sector_df.empty:
        return None
    df = sector_df.copy()
    df["total_volume"] = pd.to_numeric(df["total_volume"], errors="coerce")
    df = df.dropna(subset=["total_volume"]).sort_values("total_volume", ascending=False)
    fig = px.bar(df, x="sector", y="total_volume",
                 title="Traded Volume by Sector (latest snapshot)",
                 labels={"sector": "Sector", "total_volume": "Volume"},
                 color_discrete_sequence=["#1f77b4"])
    fig.update_layout(xaxis_tickangle=-45)
    return fig


_TITLE_STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "to", "for", "and", "with", "by",
    "from", "at", "as", "is", "its", "be", "will", "has", "have", "after",
    "new", "news", "nepal", "nepali", "npr", "rs", "company", "ltd", "limited",
}


def top_title_terms(titles, n=15):
    """Most frequent meaningful words in hydro article titles."""
    from collections import Counter
    import re as _re
    counter = Counter()
    for title in titles:
        for word in _re.findall(r"[A-Za-z]{3,}", title or ""):
            w = word.lower()
            if w not in _TITLE_STOPWORDS:
                counter[w] += 1
    if not counter:
        return None
    df = pd.DataFrame(counter.most_common(n), columns=["term", "count"])
    fig = px.bar(df.sort_values("count"), x="count", y="term", orientation="h",
                 title=f"Most Mentioned Terms in Hydro News (top {n})",
                 labels={"term": "", "count": "Mentions"},
                 color_discrete_sequence=["#032033"])
    return fig


def research_topics(research_df: pd.DataFrame):
    if research_df.empty:
        return None
    df = research_df.copy()
    topics = df["title"].str.extract(r"^(\w+)", expand=False).value_counts().reset_index()
    topics.columns = ["topic", "count"]
    fig = px.pie(topics.head(10), values="count", names="topic",
                 title="Research Report Topics")
    return fig
