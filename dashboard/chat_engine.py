from groq import Groq
from sentence_transformers import SentenceTransformer
from config import GROQ_API_KEY, GROQ_CHAT_MODEL, EMBEDDING_MODEL
from database.connection import get_conn, release_conn
from database.repository import vector_search

client = Groq(api_key=GROQ_API_KEY)
embedder = SentenceTransformer(EMBEDDING_MODEL)

TOP_K = 5
SIMILARITY_THRESHOLD = 0.35

SYSTEM_INSTRUCTION = """You are a helpful assistant that answers questions based on the provided article excerpts. Follow these rules:

1. Use the context below as your primary source. You may use general knowledge to interpret and connect information.
2. For every factual claim, cite the source article title in brackets, e.g. [Article: Title Here].
3. If the context partially answers the question, answer with what you have and note what is not covered. Do NOT say you lack information when you clearly have relevant content.
4. Be concise and direct.
5. If multiple sources support different aspects, mention all relevant sources."""


def embed_query(query):
    return embedder.encode([query])[0].tolist()


def retrieve(query):
    query_emb = embed_query(query)
    conn = get_conn()
    try:
        results = vector_search(conn, query_emb, top_k=TOP_K, threshold=SIMILARITY_THRESHOLD)
        print(f"[CHAT_DEBUG] query='{query[:50]}' threshold={SIMILARITY_THRESHOLD} chunks={len(results)}")
        return results
    finally:
        release_conn(conn)


def build_context(chunks):
    parts = []
    for i, c in enumerate(chunks):
        parts.append(f"[Source {i+1}] Article: {c['article_title']}\n{c['chunk_text']}")
    return "\n\n".join(parts)


def generate_answer(query, chunks, history=None):
    if not chunks:
        return (f"I don't have enough information about that. "
                f"(debug: threshold={SIMILARITY_THRESHOLD}, no chunks matched)"), []

    context = build_context(chunks)
    user_message = f"Context from articles:\n{context}\n\nUser question: {query}"

    resp = client.chat.completions.create(
        model=GROQ_CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
    )

    answer = resp.choices[0].message.content

    sources = []
    seen = set()
    for c in chunks:
        key = c["article_title"]
        if key not in seen:
            sources.append({"title": c["article_title"], "slug": c.get("article_slug", "")})
            seen.add(key)

    return answer, sources
