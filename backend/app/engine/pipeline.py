import time
import psycopg2.extras
from app.config import settings
from app.engine.classifier import classify_query
from app.engine.schema_linker import link_schema
from app.engine.retriever import retrieve_examples
from app.engine.generator import generate_sql
from app.engine.validator import validate_and_sanitize_sql
from app.engine.executor import execute_sql
from app.engine.formatter import format_result
from app.database.connection import execute_dml, fetch_one

def get_current_guardrails_config() -> dict:
    """Fetches active guardrails configuration from DB or defaults."""
    row = fetch_one("SELECT value FROM system_settings WHERE key = 'guardrails_config';")
    if row and row.get("value"):
        return row["value"]
    return {
        "blocked_operations": settings.BLOCKED_OPERATIONS,
        "allow_dml_override": False,
        "default_row_limit": settings.DEFAULT_ROW_LIMIT,
        "max_row_limit": settings.MAX_ROW_LIMIT,
        "enforce_row_limit": True
    }

def get_current_model_config() -> dict:
    """Fetches active model configuration from DB or defaults."""
    row = fetch_one("SELECT value FROM system_settings WHERE key = 'model_config';")
    if row and row.get("value"):
        cfg = row["value"]
        # Sync runtime API keys if stored in DB and not already in settings
        if cfg.get("groq_api_key") and not settings.GROQ_API_KEY:
            settings.GROQ_API_KEY = cfg["groq_api_key"]
        if cfg.get("gemini_api_key") and not settings.GEMINI_API_KEY:
            settings.GEMINI_API_KEY = cfg["gemini_api_key"]
        return cfg
    return {
        "default_model": settings.DEFAULT_MODEL,
        "allowed_models_for_users": settings.ALLOWED_FOR_USERS,
        "admin_enforced_model": None,
        "temperature": settings.TEMPERATURE,
        "database": "postgresql"
    }

def log_query_execution(
    query_text: str,
    generated_sql: str | None,
    query_type: str,
    status: str,
    error_message: str | None,
    latency_ms: float,
    row_count: int,
    model_used: str,
    user_email: str = "alex.rivera@subscriptiq.ai"
):
    """Logs query attempt to PostgreSQL query_logs audit table."""
    try:
        execute_dml(
            """
            INSERT INTO query_logs (
                query_text, generated_sql, query_type, status, error_message,
                latency_ms, row_count, model_used, user_email
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (query_text, generated_sql, query_type, status, error_message, latency_ms, row_count, model_used, user_email)
        )
    except Exception as e:
        print(f"Warning: could not insert into query_logs ({e})")

async def process_natural_language_query(
    query: str,
    selected_model: str | None = None,
    user_role: str = "user",
    user_email: str = "alex.rivera@subscriptiq.ai"
) -> dict:
    """
    Main Orchestrator for the 7-stage Text-to-SQL Pipeline powered by LangGraph & LangChain:
    StateGraph(NL Query -> Classifier -> Schema Linker -> Qdrant Retriever ->
    ChatGroq/ChatGoogle -> AST Validator -> MCP Postgres Executor -> Formatter).
    """
    model_cfg = get_current_model_config()
    enforced_model = model_cfg.get("admin_enforced_model")
    default_model = model_cfg.get("default_model", settings.DEFAULT_MODEL)
    allowed_models = model_cfg.get("allowed_models_for_users")
    if allowed_models is None or len(allowed_models) == 0:
        allowed_models = [m["id"] for m in settings.SUPPORTED_MODELS]

    # Effective model resolution with strict admin enforcement
    if enforced_model:
        effective_model = enforced_model
    elif selected_model and selected_model in allowed_models:
        effective_model = selected_model
    elif default_model in allowed_models:
        effective_model = default_model
    elif allowed_models:
        effective_model = allowed_models[0]
    else:
        effective_model = settings.DEFAULT_MODEL

    temperature = float(model_cfg.get("temperature", 0.1))

    # Run through the compiled LangGraph StateGraph agent
    from app.ai_services.graph import run_langgraph_pipeline
    result = await run_langgraph_pipeline(
        query=query,
        selected_model=effective_model,
        user_role=user_role,
        user_email=user_email,
        temperature=temperature
    )

    # Log query execution in query_logs audit table for Admin panel
    status = "success" if result["success"] else ("blocked" if result.get("query_type") == "UNSUPPORTED" else "error")
    log_query_execution(
        query_text=query,
        generated_sql=result.get("sql"),
        query_type=result.get("query_type", "SELECT_SIMPLE"),
        status=status,
        error_message=result.get("error"),
        latency_ms=result.get("latency_ms", 0.0),
        row_count=result.get("row_count", 0),
        model_used=effective_model,
        user_email=user_email
    )

    result["agent_connected"] = bool(settings.GROQ_API_KEY or settings.GEMINI_API_KEY)
    return result
