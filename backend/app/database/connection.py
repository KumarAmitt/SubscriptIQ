import time
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from app.config import settings

# Threaded connection pool
_pg_pool: pool.ThreadedConnectionPool | None = None

def get_connection_pool() -> pool.ThreadedConnectionPool:
    global _pg_pool
    if _pg_pool is None or _pg_pool.closed:
        _pg_pool = pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=20,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            dbname=settings.DB_NAME,
        )
    return _pg_pool

@contextmanager
def get_db_connection():
    p = get_connection_pool()
    conn = p.getconn()
    try:
        yield conn
    finally:
        p.putconn(conn)

def execute_readonly_sql(sql: str, params=None) -> dict:
    """
    Executes a SQL query in strict READ ONLY transaction mode.
    Returns:
        {
            "columns": [...],
            "rows": [...],
            "row_count": int,
            "latency_ms": float,
            "error": str | None
        }
    """
    start_time = time.perf_counter()
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Enforce read-only mode for safety at the session level
                cur.execute("SET TRANSACTION READ ONLY;")
                if params:
                    cur.execute(sql, params)
                else:
                    cur.execute(sql)
                
                rows = cur.fetchall() if cur.description else []
                columns = [desc[0] for desc in cur.description] if cur.description else []
                
                # Convert rows to plain dicts with serializable values
                clean_rows = []
                for row in rows:
                    clean_row = {}
                    for k, v in dict(row).items():
                        if hasattr(v, "isoformat"):
                            clean_row[k] = v.isoformat()
                        elif isinstance(v, (int, float, str, bool)) or v is None:
                            clean_row[k] = v
                        else:
                            clean_row[k] = str(v)
                    clean_rows.append(clean_row)
                    
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return {
                    "columns": columns,
                    "rows": clean_rows,
                    "row_count": len(clean_rows),
                    "latency_ms": latency_ms,
                    "error": None
                }
    except Exception as e:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "columns": [],
            "rows": [],
            "row_count": 0,
            "latency_ms": latency_ms,
            "error": str(e)
        }

def execute_dml(sql: str, params=None) -> None:
    """Executes DML or schema update statements with commit."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
        conn.commit()

def fetch_all(sql: str, params=None) -> list[dict]:
    """Helper to fetch rows as dictionaries."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            rows = cur.fetchall()
            return [dict(r) for r in rows]

def fetch_one(sql: str, params=None) -> dict | None:
    """Helper to fetch single row as dictionary."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            row = cur.fetchone()
            return dict(row) if row else None
