from fastapi import APIRouter, HTTPException
from app.models.schemas import SchemaColumnUpdate
from app.database.connection import fetch_all, execute_dml

router = APIRouter(prefix="/admin/schema", tags=["Admin: Schema Manager"])

@router.get("")
async def get_schema_overview():
    """
    Returns full database schema for Schema Manager:
    All tables, column data types, descriptions, sensitive flags, and row counts.
    """
    try:
        # 1. Fetch metadata table records
        meta_rows = fetch_all(
            "SELECT table_name, column_name, data_type, description, is_sensitive, synonyms FROM schema_metadata ORDER BY table_name, column_name;"
        )

        # 2. Get table row counts from actual database
        tables_to_query = [
            "organizations", "departments", "users", "vendors", "subscriptions",
            "license_allocations", "invoices", "usage_telemetry", "optimization_recommendations"
        ]
        table_counts = {}
        for tbl in tables_to_query:
            try:
                c = fetch_all(f"SELECT COUNT(*) as cnt FROM {tbl};")
                table_counts[tbl] = c[0]["cnt"] if c else 0
            except Exception:
                table_counts[tbl] = 0

        # Group by table
        tables_map = {}
        for tbl in tables_to_query:
            tables_map[tbl] = {
                "name": tbl,
                "row_count": table_counts.get(tbl, 0),
                "columns": []
            }

        for r in meta_rows:
            tbl = r["table_name"]
            if tbl not in tables_map:
                tables_map[tbl] = {
                    "name": tbl,
                    "row_count": table_counts.get(tbl, 0),
                    "columns": []
                }
            tables_map[tbl]["columns"].append({
                "column_name": r["column_name"],
                "data_type": r["data_type"],
                "description": r["description"] or "",
                "is_sensitive": bool(r["is_sensitive"]),
                "synonyms": r["synonyms"] or ""
            })

        return {
            "tables": list(tables_map.values()),
            "total_tables": len(tables_map)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/column")
async def update_column_metadata(payload: SchemaColumnUpdate):
    """
    Updates column description, sensitive flag, or synonyms in schema_metadata.
    """
    try:
        execute_dml(
            """
            INSERT INTO schema_metadata (table_name, column_name, data_type, description, is_sensitive, synonyms)
            VALUES (%s, %s, 'VARCHAR', %s, %s, %s)
            ON CONFLICT (table_name, column_name) DO UPDATE SET
                description = EXCLUDED.description,
                is_sensitive = EXCLUDED.is_sensitive,
                synonyms = EXCLUDED.synonyms,
                updated_at = CURRENT_TIMESTAMP;
            """,
            (payload.table_name, payload.column_name, payload.description, payload.is_sensitive, payload.synonyms)
        )
        return {
            "success": True,
            "message": f"Updated metadata for {payload.table_name}.{payload.column_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
