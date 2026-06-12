from datetime import datetime
from database.connection import get_conn, release_conn


def upsert_category(conn, category_id: int, name: str):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO categories (category_id, name)
               VALUES (%s, %s)
               ON CONFLICT (category_id) DO UPDATE SET name = EXCLUDED.name""",
            (category_id, name)
        )


def upsert_news_article(conn, article: dict) -> bool:
    with conn.cursor() as cur:
        posted_at = article.get("posted_at") or article.get("date")
        if posted_at and isinstance(posted_at, str):
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d"]:
                try:
                    posted_at = datetime.strptime(posted_at[:19] if len(posted_at) > 19 else posted_at, fmt)
                    break
                except ValueError:
                    continue
            else:
                posted_at = None

        category = article.get("type") or article.get("category", "")

        cur.execute(
            """INSERT INTO news_articles
               (article_id, title, sub_title, slug, summary, image, image_source,
                category, category_id, posted_at, is_hydro)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (article_id) DO UPDATE SET
                 title = EXCLUDED.title,
                 sub_title = EXCLUDED.sub_title,
                 summary = EXCLUDED.summary,
                 category = EXCLUDED.category,
                 posted_at = EXCLUDED.posted_at,
                 is_hydro = EXCLUDED.is_hydro""",
            (
                article["id"], article.get("title", ""),
                article.get("sub_title", ""), article.get("slug", ""),
                article.get("summary", ""), article.get("image", ""),
                article.get("image_source", ""),
                category, article.get("category_id"),
                posted_at, article.get("is_hydro", False),
            )
        )
    conn.commit()


def upsert_research_report(conn, report: dict) -> bool:
    with conn.cursor() as cur:
        posted_at = report.get("posted_at")
        if posted_at and isinstance(posted_at, str):
            posted_at = posted_at[:19]
            try:
                posted_at = datetime.strptime(posted_at, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                posted_at = None

        cur.execute(
            """INSERT INTO research_reports
               (expert_id, title, sub_title, slug, summary, image, image_source,
                posted_by, is_premium, posted_at, is_hydro)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (expert_id) DO UPDATE SET
                 title = EXCLUDED.title,
                 sub_title = EXCLUDED.sub_title,
                 summary = EXCLUDED.summary,
                 is_hydro = EXCLUDED.is_hydro""",
            (
                report["expert_id"], report.get("title", ""),
                report.get("sub_title", ""), report.get("slug", ""),
                report.get("summary", ""), report.get("image", ""),
                report.get("image_source", ""),
                report.get("posted_by"),
                bool(report.get("is_premium", False)),
                posted_at, report.get("is_hydro", False),
            )
        )
    conn.commit()


def get_hydro_news(conn, limit=20):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT id, article_id, title, sub_title, slug, summary, image,
                      category, posted_at, is_hydro
               FROM news_articles
               WHERE is_hydro = TRUE
               ORDER BY posted_at DESC NULLS LAST
               LIMIT %s""",
            (limit,)
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_hydro_research(conn, limit=20):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT id, expert_id, title, sub_title, slug, summary,
                      image, is_premium, posted_at, is_hydro
               FROM research_reports
               WHERE is_hydro = TRUE
               ORDER BY posted_at DESC NULLS LAST
               LIMIT %s""",
            (limit,)
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_all_hydro_companies(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, sector, symbol FROM companies WHERE is_hydro = TRUE"
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def upsert_company(conn, company: dict):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO companies (company_id, name, sector, symbol, is_hydro)
               VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT (company_id) DO UPDATE SET
                 name = EXCLUDED.name,
                 sector = EXCLUDED.sector,
                 symbol = EXCLUDED.symbol,
                 is_hydro = EXCLUDED.is_hydro""",
            (
                company.get("id"), company.get("name", ""),
                company.get("sector", ""),
                company.get("symbol", ""),
                company.get("is_hydro", False),
            )
        )
    conn.commit()


def upsert_market_data(conn, data: dict):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO market_data
               (company_id, company_name, ltp, point_change, percent_change, volume)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                data.get("company_id"), data.get("company_name"),
                data.get("ltp"), data.get("point_change"),
                data.get("percent_change"), data.get("volume"),
            )
        )
    conn.commit()


def get_latest_market_data(conn, limit=50):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT DISTINCT ON (company_name) company_name, ltp,
                      point_change, percent_change, volume, timestamp
               FROM market_data
               ORDER BY company_name, timestamp DESC
               LIMIT %s""",
            (limit,)
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_all_news(conn, limit=50, offset=0, hydro_only=False):
    with conn.cursor() as cur:
        if hydro_only:
            cur.execute(
                """SELECT id, article_id, title, sub_title, slug, summary, image,
                          category, posted_at, is_hydro
                   FROM news_articles
                   WHERE is_hydro = TRUE
                   ORDER BY posted_at DESC NULLS LAST
                   LIMIT %s OFFSET %s""",
                (limit, offset)
            )
        else:
            cur.execute(
                """SELECT id, article_id, title, sub_title, slug, summary, image,
                          category, posted_at, is_hydro
                   FROM news_articles
                   ORDER BY posted_at DESC NULLS LAST
                   LIMIT %s OFFSET %s""",
                (limit, offset)
            )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_all_news_count(conn, hydro_only=False):
    with conn.cursor() as cur:
        if hydro_only:
            cur.execute("SELECT COUNT(*) FROM news_articles WHERE is_hydro = TRUE")
        else:
            cur.execute("SELECT COUNT(*) FROM news_articles")
        return cur.fetchone()[0]


def get_all_research(conn, limit=50, offset=0, hydro_only=False):
    with conn.cursor() as cur:
        if hydro_only:
            cur.execute(
                """SELECT id, expert_id, title, sub_title, slug, summary,
                          image, is_premium, posted_at, is_hydro
                   FROM research_reports
                   WHERE is_hydro = TRUE
                   ORDER BY posted_at DESC NULLS LAST
                   LIMIT %s OFFSET %s""",
                (limit, offset)
            )
        else:
            cur.execute(
                """SELECT id, expert_id, title, sub_title, slug, summary,
                          image, is_premium, posted_at, is_hydro
                   FROM research_reports
                   ORDER BY posted_at DESC NULLS LAST
                   LIMIT %s OFFSET %s""",
                (limit, offset)
            )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_all_research_count(conn, hydro_only=False):
    with conn.cursor() as cur:
        if hydro_only:
            cur.execute("SELECT COUNT(*) FROM research_reports WHERE is_hydro = TRUE")
        else:
            cur.execute("SELECT COUNT(*) FROM research_reports")
        return cur.fetchone()[0]


def get_article_by_article_id(conn, article_id: str):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT id, article_id, title, sub_title, slug, summary, image,
                      category, posted_at, is_hydro
               FROM news_articles
               WHERE article_id = %s""",
            (article_id,)
        )
        cols = [desc[0] for desc in cur.description]
        row = cur.fetchone()
        if row:
            return dict(zip(cols, row))
        return None


def get_report_by_expert_id(conn, expert_id: int):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT id, expert_id, title, sub_title, slug, summary,
                      image, is_premium, posted_at, is_hydro
               FROM research_reports
               WHERE expert_id = %s""",
            (expert_id,)
        )
        cols = [desc[0] for desc in cur.description]
        row = cur.fetchone()
        if row:
            return dict(zip(cols, row))
        return None


def get_news_by_category(conn, category, limit=50, offset=0):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT id, article_id, title, sub_title, slug, summary, image,
                      category, posted_at, is_hydro
               FROM news_articles
               WHERE category = %s
               ORDER BY posted_at DESC NULLS LAST
               LIMIT %s OFFSET %s""",
            (category, limit, offset)
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_hydro_market_data(conn):
    """Latest market data joined to hydro companies (matched on name)."""
    with conn.cursor() as cur:
        cur.execute(
            """SELECT DISTINCT ON (m.company_name)
                      m.company_name, c.symbol, c.sector, m.ltp,
                      m.point_change, m.percent_change, m.volume, m.timestamp
               FROM market_data m
               JOIN companies c ON c.name = m.company_name
               WHERE c.is_hydro = TRUE
               ORDER BY m.company_name, m.timestamp DESC"""
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_sector_market_stats(conn):
    """Per-sector aggregates over the latest market snapshot."""
    with conn.cursor() as cur:
        cur.execute(
            """WITH latest AS (
                   SELECT DISTINCT ON (company_name)
                          company_name, ltp, percent_change, volume
                   FROM market_data
                   ORDER BY company_name, timestamp DESC
               )
               SELECT c.sector,
                      COUNT(*) AS companies,
                      AVG(l.percent_change) AS avg_percent_change,
                      SUM(l.volume) AS total_volume
               FROM latest l
               JOIN companies c ON c.name = l.company_name
               WHERE c.sector IS NOT NULL AND c.sector != ''
               GROUP BY c.sector
               ORDER BY companies DESC"""
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_monthly_hydro_news_counts(conn):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT date_trunc('month', posted_at) AS month, COUNT(*) AS count
               FROM news_articles
               WHERE is_hydro = TRUE AND posted_at IS NOT NULL
               GROUP BY 1
               ORDER BY 1"""
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_hydro_news_titles(conn, limit=2000):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT title FROM news_articles
               WHERE is_hydro = TRUE
               ORDER BY posted_at DESC NULLS LAST
               LIMIT %s""",
            (limit,)
        )
        return [row[0] for row in cur.fetchall()]


def get_news_count_by_category(conn, category):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM news_articles WHERE category = %s", (category,))
        return cur.fetchone()[0]


def get_news_category_counts(conn):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT category, COUNT(*) as count
               FROM news_articles
               WHERE category IS NOT NULL AND category != ''
               GROUP BY category
               ORDER BY count DESC"""
        )
        return cur.fetchall()


def get_unprocessed_articles(conn):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT na.article_id, na.title, na.slug, na.summary
               FROM news_articles na
               WHERE NOT EXISTS (
                   SELECT 1 FROM article_chunks ac WHERE ac.article_id = na.article_id
               )
               ORDER BY na.posted_at DESC"""
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def store_chunks(conn, chunks):
    with conn.cursor() as cur:
        for c in chunks:
            cur.execute(
                """INSERT INTO article_chunks
                   (article_id, chunk_index, chunk_text, article_title, article_slug, embedding)
                   VALUES (%s, %s, %s, %s, %s, %s::vector)
                   ON CONFLICT (article_id, chunk_index) DO UPDATE SET
                     chunk_text = EXCLUDED.chunk_text,
                     embedding = EXCLUDED.embedding""",
                (
                    c["article_id"], c["chunk_index"], c["chunk_text"],
                    c["article_title"], c["article_slug"],
                    c["embedding"],
                )
            )
    conn.commit()


def vector_search(conn, query_embedding, top_k=5, threshold=0.75):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT ac.id, ac.chunk_text, ac.article_title, ac.article_slug,
                      ac.article_id, na.posted_at,
                      1 - (ac.embedding <=> %s::vector) AS similarity
               FROM article_chunks ac
               JOIN news_articles na ON na.article_id = ac.article_id
               WHERE 1 - (ac.embedding <=> %s::vector) >= %s
               ORDER BY similarity DESC
               LIMIT %s""",
            (query_embedding, query_embedding, threshold, top_k)
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def count_chunks(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM article_chunks")
        return cur.fetchone()[0]


def count_articles_embedded(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(DISTINCT article_id) FROM article_chunks")
        return cur.fetchone()[0]
