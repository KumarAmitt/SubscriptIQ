from app.database.connection import execute_readonly_sql

def execute_sql(sanitized_sql: str) -> dict:
    """
    Step 6: SQL Executor
    Executes the validated SQL query against PostgreSQL in read-only transaction mode.
    Returns:
        {
            "columns": list[str],
            "rows": list[dict],
            "row_count": int,
            "latency_ms": float,
            "error": str | None
        }
    """
    return execute_readonly_sql(sanitized_sql)
