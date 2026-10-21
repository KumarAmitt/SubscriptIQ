from fastapi import APIRouter, HTTPException
import psycopg2.extras
from app.models.schemas import ModelConfigModel
from app.database.connection import fetch_one, execute_dml
from app.config import settings

router = APIRouter(prefix="/admin/config", tags=["Admin: Model & Environment Config"])

@router.get("")
async def get_config():
    """
    Returns AI model settings, allowed models, admin defaults, and dialect.
    """
    try:
        row = fetch_one("SELECT value FROM system_settings WHERE key = 'model_config';")
        cfg = row["value"] if (row and row.get("value")) else {}
        
        return {
            "supported_models": settings.SUPPORTED_MODELS,
            "default_model": cfg.get("default_model", settings.DEFAULT_MODEL),
            "allowed_models_for_users": cfg.get("allowed_models_for_users", settings.ALLOWED_FOR_USERS),
            "admin_enforced_model": cfg.get("admin_enforced_model", None),
            "temperature": cfg.get("temperature", settings.TEMPERATURE),
            "database_engine": "postgresql",
            "max_tokens": cfg.get("max_tokens", 1024),
            "groq_api_key_set": bool(settings.GROQ_API_KEY or cfg.get("groq_api_key")),
            "gemini_api_key_set": bool(settings.GEMINI_API_KEY or cfg.get("gemini_api_key")),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def update_config(payload: ModelConfigModel):
    """
    Updates AI model configurations, admin default model, user allowed models,
    and credentials.
    """
    try:
        val = payload.model_dump()
        
        # Retrieve existing config to avoid erasing existing keys if left blank
        row = fetch_one("SELECT value FROM system_settings WHERE key = 'model_config';")
        existing_cfg = row["value"] if (row and row.get("value")) else {}

        if not payload.groq_api_key and existing_cfg.get("groq_api_key"):
            val["groq_api_key"] = existing_cfg["groq_api_key"]
            settings.GROQ_API_KEY = existing_cfg["groq_api_key"]
        elif payload.groq_api_key:
            settings.GROQ_API_KEY = payload.groq_api_key

        if not payload.gemini_api_key and existing_cfg.get("gemini_api_key"):
            val["gemini_api_key"] = existing_cfg["gemini_api_key"]
            settings.GEMINI_API_KEY = existing_cfg["gemini_api_key"]
        elif payload.gemini_api_key:
            settings.GEMINI_API_KEY = payload.gemini_api_key

        # Ensure default_model is consistent with allowed_models_for_users
        allowed = val.get("allowed_models_for_users") or []
        default_m = val.get("default_model")
        if len(allowed) == 1:
            val["default_model"] = allowed[0]
        elif allowed and default_m and default_m not in allowed:
            val["default_model"] = allowed[0]

        execute_dml(
            """
            INSERT INTO system_settings (key, value)
            VALUES ('model_config', %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP;
            """,
            (psycopg2.extras.Json(val),)
        )
        return {
            "success": True,
            "message": "AI model configuration updated successfully.",
            "agent_connected": bool(settings.GROQ_API_KEY or settings.GEMINI_API_KEY),
            "config": val
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
