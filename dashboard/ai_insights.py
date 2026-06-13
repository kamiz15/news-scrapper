import streamlit as st
import pandas as pd
from groq import Groq
from config import GROQ_API_KEY, GROQ_CHAT_MODEL

client = Groq(api_key=GROQ_API_KEY)


def _call_groq(system, user, temperature=0.3):
    resp = client.chat.completions.create(
        model=GROQ_CHAT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content


@st.cache_data(ttl=3600, show_spinner=False)
def market_brief(market_df: pd.DataFrame) -> str:
    if market_df.empty:
        return "No market data available."

    total = len(market_df)
    gainers = (market_df["percent_change"] > 0).sum()
    losers = (market_df["percent_change"] < 0).sum()
    unchanged = total - gainers - losers
    avg_change = market_df["percent_change"].mean()
    best = market_df.loc[market_df["percent_change"].idxmax()]
    worst = market_df.loc[market_df["percent_change"].idxmin()]
    volume_leader = market_df.loc[market_df["volume"].idxmax()]

    data_summary = f"""Total companies: {total}
Gainers: {gainers} | Losers: {losers} | Unchanged: {unchanged}
Average % change: {avg_change:+.2f}%
Biggest gainer: {best['company_name']} ({best['percent_change']:+.2f}%)
Biggest loser: {worst['company_name']} ({worst['percent_change']:+.2f}%)
Volume leader: {volume_leader['company_name']} (volume: {volume_leader['volume']})"""

    system = "You are a concise market analyst. Summarize the hydropower market in 2-3 sentences based on the data provided. Be factual and direct."
    return _call_groq(system, data_summary)


def news_impact_analysis(news_df: pd.DataFrame, market_df: pd.DataFrame) -> str:
    if news_df.empty:
        return "No recent news articles to analyze."

    news_lines = []
    for _, a in news_df.head(15).iterrows():
        title = a.get("title", "")
        summary = a.get("summary", "")
        snippet = (summary[:200] + "...") if len(str(summary)) > 200 else summary
        news_lines.append(f"- {title}\n  {snippet}")

    market_lines = []
    for _, m in market_df.iterrows():
        market_lines.append(f"- {m['company_name']}: {m['percent_change']:+.2f}% (LTP: {m['ltp']})")

    context = f"""Recent News Articles:
{chr(10).join(news_lines)}

Market Data:
{chr(10).join(market_lines)}"""

    system = "You are a financial journalist. Analyze the recent news and market data, then write a 1-paragraph analysis connecting news themes to market movements. Mention specific article titles and companies where relevant. Be insightful but concise."
    return _call_groq(system, context)


def sector_pulse(news_df: pd.DataFrame) -> dict:
    if news_df.empty:
        return {"overall_sentiment": "neutral", "key_themes": ["No data"], "article_ids_recommended": []}

    news_lines = []
    for _, a in news_df.head(30).iterrows():
        title = a.get("title", "")
        summary = a.get("summary", "")
        snippet = (summary[:150] + "...") if len(str(summary)) > 150 else summary
        news_lines.append(f"[{a.get('article_id', '')}] {title}\n  {snippet}")

    context = "Analyze these hydropower news articles:\n\n" + "\n".join(news_lines)

    system = """Analyze the given hydropower news articles and return ONLY a valid JSON object with these fields:
1. "overall_sentiment": "positive", "neutral", or "negative"
2. "key_themes": array of 3-5 themes found across the articles (short phrases like "Debt concerns", "Policy changes", "Construction updates")
3. "article_ids_recommended": array of 2-3 article IDs (from the brackets) most worth reading

Example: {"overall_sentiment": "neutral", "key_themes": ["Debt concerns", "NEA policy", "Company results"], "article_ids_recommended": ["abc123", "def456"]}

Return ONLY the JSON, no other text."""

    import json
    try:
        raw = _call_groq(system, context, temperature=0.1)
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("\n", 1)[0]
            if raw.endswith("```"):
                raw = raw[:-3]
        return json.loads(raw)
    except Exception:
        return {"overall_sentiment": "neutral", "key_themes": ["Analysis unavailable"], "article_ids_recommended": []}
