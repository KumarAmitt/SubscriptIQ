from fastapi import APIRouter, HTTPException
import psycopg2.extras
from app.models.schemas import GuardrailsConfigModel
from app.database.connection import fetch_one, execute_dml
from app.config import settings

router = APIRouter(prefix="/admin/guardrails", tags=["Admin: Guardrails Config"])

@router.get("")
async def get_guardrails():
    """Returns current active guardrails settings."""
    try:
        row = fetch_one("SELECT value FROM system_settings WHERE key = 'guardrails_config';")
        if row and row.get("value"):
            return row["value"]
        return {
            "blocked_operations": settings.BLOCKED_OPERATIONS,
            "allow_dml_override": False,
            "default_row_limit": settings.DEFAULT_ROW_LIMIT,
            "max_row_limit": settings.MAX_ROW_LIMIT,
            "enforce_row_limit": True,
            "allowed_tables": [
                "organizations", "departments", "users", "vendors",
                "subscriptions", "license_allocations", "invoices",
                "usage_telemetry", "optimization_recommendations"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def update_guardrails(payload: GuardrailsConfigModel):
    """Updates guardrails configuration and persists to system_settings."""
    try:
        val = payload.model_dump()
        execute_dml(
            """
            INSERT INTO system_settings (key, value)
            VALUES ('guardrails_config', %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP;
            """,
            (psycopg2.extras.Json(val),)
        )
        return {
            "success": True,
            "message": "Guardrails configuration successfully updated.",
            "config": val
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
