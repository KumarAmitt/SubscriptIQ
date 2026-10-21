import csv
import io
from fastapi import APIRouter, HTTPException, Query, Response
from app.database.connection import fetch_all, execute_dml

router = APIRouter(prefix="/admin/logs", tags=["Admin: Query Logs"])

@router.get("")
async def get_logs(
    status: str | None = Query(None, description="Filter by status: 'success', 'error', 'blocked'"),
    search: str | None = Query(None, description="Search query text or SQL"),
    limit: int = Query(50, ge=1, le=200)
):
    """
    Returns query execution audit logs with filtering and execution metrics.
    """
    try:
        query_sql = "SELECT id, query_text, generated_sql, query_type, status, error_message, latency_ms, row_count, model_used, user_email, created_at FROM query_logs"
        conditions = []
        params = []

        if status:
            conditions.append("status = %s")
            params.append(status)

        if search and search.strip():
            conditions.append("(query_text ILIKE %s OR generated_sql ILIKE %s)")
            params.extend([f"%{search.strip()}%", f"%{search.strip()}%"])

        if conditions:
            query_sql += " WHERE " + " AND ".join(conditions)

        query_sql += " ORDER BY created_at DESC LIMIT %s;"
        params.append(limit)

        logs = fetch_all(query_sql, tuple(params))
        return {
            "logs": logs,
            "count": len(logs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("")
async def clear_logs():
    """Clears all query logs."""
    try:
        execute_dml("TRUNCATE TABLE query_logs;")
        return {"success": True, "message": "All query logs cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export")
async def export_logs_csv():
    """Exports query logs as downloadable CSV."""
    try:
        logs = fetch_all("SELECT * FROM query_logs ORDER BY created_at DESC LIMIT 500;")
        output = io.StringIO()
        if logs:
            writer = csv.DictWriter(output, fieldnames=logs[0].keys())
            writer.writeheader()
            writer.writerows(logs)
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=query_logs.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
