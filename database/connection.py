import os
import psycopg2
from psycopg2 import pool
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

_connection_pool = None


def get_pool():
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = pool.ThreadedConnectionPool(
            minconn=1, maxconn=10,
            host=DB_HOST, port=DB_PORT,
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
    return _connection_pool


def get_conn():
    return get_pool().getconn()


def release_conn(conn):
    get_pool().putconn(conn)


def init_db():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
            with open(schema_path, "r") as f:
                cur.execute(f.read())
        conn.commit()
    finally:
        release_conn(conn)
