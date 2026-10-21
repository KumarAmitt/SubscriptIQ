"""
Model Context Protocol (MCP) Compatible Database Tools for PostgreSQL.
Decorated using LangChain's @tool decorator for native tool calling and schema exposure.
"""
from typing import Dict, Any, List
from langchain_core.tools import tool
from app.database.connection import execute_readonly_sql, fetch_all, fetch_one

@tool
def mcp_postgres_query(sql_query: str) -> Dict[str, Any]:
    """
    MCP Database Tool: Execute a read-only SELECT query against the enterprise PostgreSQL database.
    
    Args:
        sql_query: The SQL query statement to execute. Must be a safe, read-only SELECT statement.
        
    Returns:
        Dict containing success status, column headers, returned records, and row count.
    """
    clean_sql = sql_query.strip()
    if not clean_sql.upper().startswith("SELECT") and not clean_sql.upper().startswith("WITH"):
        return {
            "success": False,
            "error": "Security Violation: Only read-only SELECT queries are permitted by MCP guardrails.",
            "columns": [],
            "rows": [],
            "row_count": 0
        }

    exec_result = execute_readonly_sql(clean_sql)
    return {
        "success": exec_result.get("error") is None,
        "error": exec_result.get("error"),
        "columns": exec_result.get("columns", []),
        "rows": exec_result.get("rows", []),
        "row_count": exec_result.get("row_count", 0),
        "latency_ms": exec_result.get("latency_ms", 0.0)
    }

@tool
def mcp_get_table_schema(table_name: str) -> Dict[str, Any]:
    """
    MCP Database Tool: Inspect the PostgreSQL schema metadata, columns, and data types for a given table.
    
    Args:
        table_name: Name of the relational table to inspect.
    """
    try:
        query = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
        """
        rows = fetch_all(query, (table_name.lower(),))
        return {
            "table_name": table_name,
            "columns": rows
        }
    except Exception as e:
        return {
            "table_name": table_name,
            "error": str(e)
        }

@tool
def mcp_explain_query(sql_query: str) -> str:
    """
    MCP Database Tool: Run PostgreSQL EXPLAIN on a SQL statement to verify execution plan and syntax.
    
    Args:
        sql_query: The SQL query to explain.
    """
    try:
        row = fetch_one(f"EXPLAIN {sql_query}")
        return row.get("QUERY PLAN", "Plan generated") if row else "No plan returned."
    except Exception as e:
        return f"Explain error: {e}"

# Registered MCP database tools
mcp_database_tools = [
    mcp_postgres_query,
    mcp_get_table_schema,
    mcp_explain_query
]
