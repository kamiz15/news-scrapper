import logging
from sentence_transformers import SentenceTransformer
from config import clean_html, EMBEDDING_MODEL
from database.connection import get_conn, release_conn
from database.repository import get_unprocessed_articles, store_chunks, count_chunks, count_articles_embedded

logger = logging.getLogger(__name__)

model = SentenceTransformer(EMBEDDING_MODEL)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


def embed_texts(texts):
    if not texts:
        return []
    return model.encode(texts).tolist()


def ingest_all():
    conn = get_conn()
    try:
        articles = get_unprocessed_articles(conn)
        if not articles:
            logger.info("No new articles to process.")
            return

        total_chunks = 0
        for art in articles:
            text = clean_html(art["summary"])
            if not text.strip():
                text = clean_html(art.get("sub_title", ""))
            if not text.strip():
                text = art["title"]
            text = f"{art['title']}\n\n{text}"
            chunks = chunk_text(text)
            if not chunks:
                continue

            embeddings = embed_texts(chunks)

            rows = []
            for i, (txt, emb) in enumerate(zip(chunks, embeddings)):
                rows.append({
                    "article_id": art["article_id"],
                    "chunk_index": i,
                    "chunk_text": txt,
                    "article_title": art["title"],
                    "article_slug": art.get("slug", ""),
                    "embedding": emb,
                })
            store_chunks(conn, rows)
            total_chunks += len(rows)
            logger.info("  %s → %d chunks", art["article_id"], len(rows))

        c = count_chunks(conn)
        a = count_articles_embedded(conn)
        logger.info("Done. %d chunks across %d articles (total)", c, a)
    finally:
        release_conn(conn)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ingest_all()
