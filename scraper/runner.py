import logging
import os
import time
from scraper.api_client import ApiClient
from scraper.hydro_filter import is_hydro_text, is_hydro_company
from database.repository import (
    upsert_category, upsert_news_article, upsert_research_report,
    upsert_company, upsert_market_data,
)
from database.connection import get_conn, release_conn, init_db

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scraper.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

client = ApiClient()


def scrape_categories():
    conn = get_conn()
    try:
        categories = client.get_categories()
        for cat in categories:
            upsert_category(conn, cat["category_id"], cat["category"])
        logger.info("Scraped %d categories", len(categories))
    finally:
        release_conn(conn)


def scrape_all_news():
    conn = get_conn()
    total = 0
    hydro_total = 0
    page = 1
    prev_first_id = None
    try:
        while True:
            data = client.get_all_posts(page=page, limit=50)
            articles = data.get("data", {}).get("data", [])
            if not articles:
                break
            first_id = articles[0].get("id")
            if first_id is not None and first_id == prev_first_id:
                logger.warning("News page %d returned same data as previous page; stopping.", page)
                break
            prev_first_id = first_id
            for article in articles:
                text = f"{article.get('title', '')} {article.get('summary', '')} {article.get('sub_title', '')}"
                article["is_hydro"] = is_hydro_text(text)
                if article["is_hydro"]:
                    hydro_total += 1
                upsert_news_article(conn, article)
            total += len(articles)
            logger.info("News page %d: %d articles (total: %d, hydro: %d)", page, len(articles), total, hydro_total)
            page += 1
        logger.info("=== All news done: %d total (%d hydro) ===", total, hydro_total)
        return total
    finally:
        release_conn(conn)


def scrape_all_research():
    conn = get_conn()
    total = 0
    hydro_total = 0
    page = 1
    prev_first_id = None
    try:
        while True:
            data = client.get_research_reports(page=page, limit=50)
            reports = data.get("data", [])
            if not reports:
                break
            first_id = reports[0].get("expert_id")
            if first_id is not None and first_id == prev_first_id:
                logger.warning("Research page %d returned same data as previous page; stopping.", page)
                break
            prev_first_id = first_id
            for report in reports:
                text = f"{report.get('title', '')} {report.get('summary', '')} {report.get('sub_title', '')}"
                report["is_hydro"] = is_hydro_text(text)
                if report["is_hydro"]:
                    hydro_total += 1
                upsert_research_report(conn, report)
            total += len(reports)
            logger.info("Research page %d: %d reports (total: %d, hydro: %d)", page, len(reports), total, hydro_total)
            page += 1
        logger.info("=== All research done: %d total (%d hydro) ===", total, hydro_total)
        return total
    finally:
        release_conn(conn)


def scrape_companies():
    conn = get_conn()
    try:
        data = client.get_company_search()
        companies = data.get("data", [])
        hydro_count = 0
        for company in companies:
            company["is_hydro"] = is_hydro_company(
                company.get("company_name", ""), company.get("sector_name", "")
            )
            if company["is_hydro"]:
                hydro_count += 1
            upsert_company(conn, {
                "id": company.get("company_id"),
                "name": company.get("company_name", ""),
                "sector": company.get("sector_name", ""),
                "symbol": company.get("symbol", ""),
                "is_hydro": company["is_hydro"],
            })
        logger.info("Scraped %d companies (%d hydro)", len(companies), hydro_count)
    finally:
        release_conn(conn)


def scrape_market():
    conn = get_conn()
    try:
        data = client.get_market_data()
        if hasattr(data, "json"):
            data = data.json()
        items = data.get("data", [])
        count = 0
        for item in items:
            if "company_name" in item:
                upsert_market_data(conn, {
                    "company_id": item.get("market_id"),
                    "company_name": item.get("company_name", ""),
                    "ltp": item.get("current"),
                    "point_change": item.get("point_change"),
                    "percent_change": item.get("percentage_change"),
                    "volume": item.get("turnover"),
                })
                count += 1
        logger.info("Scraped %d market data points (%d companies)", len(items), count)
    finally:
        release_conn(conn)


def run_all(progress_callback=None):
    if progress_callback:
        progress_callback("Initializing database...", 0)
    init_db()

    if progress_callback:
        progress_callback("Scraping categories...", 5)
    scrape_categories()

    if progress_callback:
        progress_callback("Scraping companies...", 10)
    scrape_companies()

    if progress_callback:
        progress_callback("Scraping all news articles (this may take a while)...", 20)
    total_news = scrape_all_news()

    if progress_callback:
        progress_callback("Scraping all research reports...", 60)
    total_research = scrape_all_research()

    if progress_callback:
        progress_callback("Scraping market data...", 90)
    scrape_market()

    if progress_callback:
        progress_callback("Generating embeddings for chatbot...", 95)
    from scraper.ingest import ingest_all
    ingest_all()

    msg = f"Scrape complete: {total_news} news, {total_research} research"
    if progress_callback:
        progress_callback(msg, 100)
    logger.info("=== %s ===", msg)
