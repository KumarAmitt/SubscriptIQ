from pydantic import BaseModel, Field
from typing import Any

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language question from the user")
    model_id: str | None = Field(None, description="Optional chosen AI model")
    user_role: str = Field("user", description="'user' or 'admin'")
    user_email: str = Field("alex.rivera@subscriptiq.ai", description="User email for audit logging")

class QueryResponse(BaseModel):
    success: bool
    query: str
    query_type: str
    model_used: str
    sql: str | None = None
    explanation: str | None = None
    nl_summary: str
    columns: list[str] = []
    rows: list[dict[str, Any]] = []
    row_count: int = 0
    latency_ms: float = 0.0
    execution_latency_ms: float = 0.0
    chart: dict[str, Any] | None = None
    transpiled: dict[str, str] = {}
    pipeline_steps: dict[str, Any] = {}
    error: str | None = None
    agent_connected: bool = False

class SchemaColumnUpdate(BaseModel):
    table_name: str
    column_name: str
    description: str | None = None
    is_sensitive: bool = False
    synonyms: str | None = None

class FewShotExampleItem(BaseModel):
    id: int | None = None
    question: str
    sql: str
    query_type: str
    explanation: str | None = None

class GuardrailsConfigModel(BaseModel):
    blocked_operations: list[str] = ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER", "GRANT", "REVOKE", "CREATE"]
    allow_dml_override: bool = False
    default_row_limit: int = 1000
    max_row_limit: int = 2000
    enforce_row_limit: bool = False
    allowed_tables: list[str] = []

class ModelConfigModel(BaseModel):
    default_model: str = "openai/gpt-oss-120b"
    allowed_models_for_users: list[str] = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "gemini-3.1-flash-lite",
        "gemma-4-26b-a4b-it"
    ]
    admin_enforced_model: str | None = None
    temperature: float = 0.1
    max_tokens: int = 1024
    groq_api_key: str | None = None
    gemini_api_key: str | None = None
